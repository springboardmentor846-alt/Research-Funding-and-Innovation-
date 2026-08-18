"""Patent ingestion service.

Takes a list of ``NormalizedPatent`` (one provider's contribution to a
batch) and merges them into the canonical ``Patent`` table, using the
existing quality helpers in ``app.patents.quality`` for normalization,
validation, and cross-source deduplication.

Behaviour
---------

* Validates every record with ``is_valid_patent_record``; rejects
  records with no patent_number / title / abstract-or-keywords.
* Looks up an existing row by ``lens_id`` first (Lens rows carry a
  unique ``lens_id`` so that is the canonical key).  Falls back to
  ``(source, source_id)`` for non-Lens providers, and finally to a
  canonical ``patent_number`` lookup.  This ordering matters: the
  Lens API sometimes returns the same invention under slightly
  different numbers, so dedup needs the lens_id short-circuit.
* When a duplicate is detected, calls ``decide_merge`` and applies
  the merge delta non-destructively.  The ``last_synced_at`` column
  is always refreshed so incremental sync can re-fetch only newer
  patents on the next run.
* Tracks per-run counters so the SyncEngine can fold them into the
  ``PatentSyncRun`` row.
* Catches ``IntegrityError`` from the ``uq_patents_lens_id`` unique
  index and re-tries as an update — defence-in-depth in case two
  coroutines ingested the same Lens id concurrently.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.models.patent import Patent
from app.patents.core.base import NormalizedPatent
from app.patents.quality.normalization import detect_technology_area
from app.patents.quality.deduplication import decide_merge
from app.patents.quality.validation import is_valid_patent_record


@dataclass
class IngestReport:
    """Per-run counters for the ingest service."""

    fetched: int = 0
    inserted: int = 0
    updated: int = 0
    skipped: int = 0
    duplicates_removed: int = 0
    errors: List[Dict[str, str]] = field(default_factory=list)

    def merge(self, other: "IngestReport") -> None:
        self.fetched += other.fetched
        self.inserted += other.inserted
        self.updated += other.updated
        self.skipped += other.skipped
        self.duplicates_removed += other.duplicates_removed
        self.errors.extend(other.errors)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fetched": self.fetched,
            "inserted": self.inserted,
            "updated": self.updated,
            "skipped": self.skipped,
            "duplicates_removed": self.duplicates_removed,
            "errors": self.errors,
        }


class PatentIngestService:
    """Stateless service that turns provider batches into DB rows."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------
    def ingest(self, normalized: List[NormalizedPatent]) -> IngestReport:
        report = IngestReport()
        sync_ts = datetime.utcnow()
        for record in normalized:
            report.fetched += 1
            try:
                outcome = self._ingest_one(record, sync_ts=sync_ts)
                if outcome == "inserted":
                    report.inserted += 1
                elif outcome == "updated":
                    report.updated += 1
                elif outcome == "skipped":
                    report.skipped += 1
                elif outcome == "merged":
                    report.duplicates_removed += 1
            except Exception as exc:  # pragma: no cover - defensive
                logger.exception(f"[ingest] record failed: {exc}")
                report.errors.append(
                    {"record_id": str(record.source_id), "message": str(exc)[:500]}
                )
                report.skipped += 1
        # Commit once per batch — the SyncEngine opens one transaction
        # per provider; we don't want to leave a half-applied batch.
        try:
            self.db.commit()
        except Exception as exc:
            self.db.rollback()
            logger.exception(f"[ingest] commit failed: {exc}")
            for record in normalized:
                report.errors.append(
                    {
                        "record_id": str(record.source_id),
                        "message": f"commit failed: {exc}",
                    }
                )
        return report

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _ingest_one(
        self, record: NormalizedPatent, *, sync_ts: datetime
    ) -> str:
        """Return one of: 'inserted', 'updated', 'merged', 'skipped'."""
        create_dict = record.to_patent_create_dict()
        # Always stamp the sync time so incremental sync works
        # regardless of what the provider supplied.
        create_dict["last_synced_at"] = sync_ts

        # If the provider didn't populate technology_area, fill in a
        # CPC-prefix-based label so the dashboard isn't blank.
        if not create_dict.get("technology_area"):
            tech_area = detect_technology_area(
                create_dict.get("classification")
            )
            if tech_area:
                create_dict["technology_area"] = tech_area

        valid, reason = is_valid_patent_record(create_dict)
        if not valid:
            logger.info(f"[ingest] skip {record.source_id}: {reason}")
            return "skipped"

        lens_id = self._extract_lens_id(record, create_dict)

        # 1. Lens_id shortcut — the canonical Lens key.
        if lens_id:
            existing = (
                self.db.query(Patent)
                .filter(Patent.lens_id == lens_id)
                .one_or_none()
            )
            if existing is not None:
                self._apply_merge(existing, create_dict, sync_ts=sync_ts)
                return "updated"

        # 2. Provider-side identity (source, source_id).
        existing = (
            self.db.query(Patent)
            .filter(Patent.source == record.source)
            .filter(Patent.source_id == record.source_id)
            .one_or_none()
        )
        if existing is not None:
            self._apply_merge(existing, create_dict, sync_ts=sync_ts)
            return "updated"

        # 3. Cross-source dedup on canonical patent_number.
        existing_by_number = (
            self.db.query(Patent)
            .filter(Patent.patent_number == create_dict["patent_number"])
            .one_or_none()
        )
        if existing_by_number is not None:
            incoming = create_dict
            existing_dict = {
                k: getattr(existing_by_number, k, None)
                for k in (
                    "title", "abstract", "inventors", "assignee",
                    "technology_area", "keywords", "country",
                    "classification", "classification_label",
                    "filing_date", "publication_date", "publication_year",
                    "citations", "patent_family", "legal_status", "url",
                    "applicant_names", "inventor_names", "jurisdiction",
                    "lens_id",
                )
            }
            decision = decide_merge(incoming=incoming, existing=existing_dict)
            if decision.is_duplicate:
                self._apply_merge(
                    existing_by_number, decision.merge_fields, sync_ts=sync_ts
                )
                return "merged"
            return self._insert_new(create_dict)

        return self._insert_new(create_dict)

    def _insert_new(self, create_dict: Dict[str, Any]) -> str:
        row = Patent(**create_dict)
        self.db.add(row)
        try:
            self.db.flush()
            # Race against the partial unique index on
            # ``patents.lens_id`` — if a concurrent ingestion won the
            # race the flush raises IntegrityError.  Roll back the
            # half-applied row and re-fetch the winner for an
            # in-place update.
        except IntegrityError as exc:
            self.db.rollback()
            logger.info(
                f"[ingest] lens_id unique violation, attempting update: {exc}"
            )
            lens_id = create_dict.get("lens_id")
            if not lens_id:
                logger.warning("[ingest] integrity error without lens_id; skipping")
                return "skipped"
            winner = (
                self.db.query(Patent)
                .filter(Patent.lens_id == lens_id)
                .one_or_none()
            )
            if winner is None:
                logger.warning(
                    f"[ingest] lost lens_id race but no winner row found: {lens_id}"
                )
                return "skipped"
            self._apply_merge(
                winner, create_dict, sync_ts=create_dict.get("last_synced_at")
            )
            return "updated"
        except Exception as exc:
            self.db.rollback()
            logger.exception(f"[ingest] insert failed: {exc}")
            return "skipped"
        return "inserted"

    def _apply_merge(
        self,
        existing: Patent,
        merge_fields: Dict[str, Any],
        *,
        sync_ts: Optional[datetime] = None,
    ) -> None:
        for k, v in merge_fields.items():
            if k == "extra_metadata" and isinstance(v, dict):
                # Merge metadata dicts non-destructively.
                existing_meta = dict(existing.extra_metadata or {})
                existing_meta.update(
                    {
                        k2: v2
                        for k2, v2 in v.items()
                        if v2 not in (None, "", [], {})
                    }
                )
                existing.extra_metadata = existing_meta or None
                continue
            if v in (None, "", []):
                continue
            if hasattr(existing, k):
                setattr(existing, k, v)
        # Always refresh ``last_synced_at`` so incremental sync has a
        # current cursor on the next run.
        if sync_ts is not None:
            existing.last_synced_at = sync_ts
        elif hasattr(existing, "last_synced_at"):
            existing.last_synced_at = datetime.utcnow()
        try:
            self.db.flush()
        except IntegrityError:
            # A second ingest of the same row raced us.  Drop the
            # half-applied change — the other writer already has the
            # authoritative copy.
            self.db.rollback()
        except Exception as exc:  # pragma: no cover - defensive
            self.db.rollback()
            logger.exception(f"[ingest] merge failed: {exc}")

    @staticmethod
    def _extract_lens_id(
        record: NormalizedPatent, create_dict: Dict[str, Any]
    ) -> Optional[str]:
        lens_id = create_dict.get("lens_id")
        if lens_id:
            return str(lens_id)
        # ``source_id`` is set to ``lens_id or publication_number``
        # for the Lens provider.  Only treat it as a lens id if it
        # actually looks like one (Lens ids are alphanumerics, but the
        # publication_number could be like "US12345678B2").
        if record.source == "the_lens" and isinstance(record.source_id, str):
            sid = record.source_id.strip()
            # Lens ids are short hash-like strings; publication
            # numbers contain a country prefix.
            if sid and not sid.upper().startswith(
                ("US", "EP", "WO", "JP", "CN", "KR", "DE", "GB", "FR")
            ):
                return sid
        return None
