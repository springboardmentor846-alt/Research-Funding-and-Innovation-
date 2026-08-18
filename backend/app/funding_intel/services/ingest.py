"""Ingestion service: persists ``NormalizedFunding`` records.

Responsibilities
----------------
* Open / re-open a ``Funding`` row keyed by ``(source, source_id)``.
* Apply field-level validation and dedup folding.
* Mark expired rows ``is_active=False`` so they drop out of
  recommendations.
* Track every action in a ``SyncRun`` aggregate (records fetched,
  inserted, updated, skipped, duplicates, expired).

The ingest service is fully synchronous (it talks to a SQLAlchemy
session). It is invoked from the async sync engine (``services.sync``)
which handles provider iteration and error isolation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Iterable, List, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.funding_intel.core.base import NormalizedFunding
from app.funding_intel.models import FundingSource, SyncRun, SyncRunError
from app.funding_intel.quality import (
    compute_status,
    is_duplicate,
    merge_normalized,
    validate_normalized,
    ValidationError,
)
from app.funding_intel.quality.deduplication import title_similarity
from app.models.funding import Funding


_SUMMARY_MAX = 280


@dataclass
class IngestStats:
    """Per-run counters for the ingest stage."""

    inserted: int = 0
    updated: int = 0
    skipped: int = 0
    duplicates: int = 0
    expired: int = 0
    errors: List[str] = field(default_factory=list)
    # IDs of funding rows newly inserted during this run.  Used by
    # the notification hook to fire FUNDING_NEW / FUNDING_MATCH alerts
    # without disturbing the rest of the ingest path.
    inserted_funding_ids: List[int] = field(default_factory=list)


class IngestService:
    """Stateless helper that turns ``NormalizedFunding`` into DB rows."""

    def __init__(self, db: Session, run: SyncRun):
        self.db = db
        self.run = run
        self.stats = IngestStats()

    # ------------------------------------------------------------------
    # Public entry points
    # ------------------------------------------------------------------
    def ingest_batch(self, records: Iterable[NormalizedFunding]) -> IngestStats:
        for raw in records:
            try:
                self._ingest_one(raw)
            except Exception as exc:  # pragma: no cover - defensive
                # Never let a single bad record crash the batch.
                logger.exception(f"[{self.run.provider}] ingest error: {exc}")
                self.stats.errors.append(str(exc))
                self._record_error("ingest", getattr(raw, "source_id", None), str(exc))
        self._commit()
        # Fire FUNDING_NEW / FUNDING_MATCH notifications for any rows
        # that were just inserted.  Best-effort: a notification failure
        # is logged but never propagated.
        if self.stats.inserted_funding_ids:
            try:
                from app.services.notification_service import (
                    run_new_funding_alert_for,
                )
                for fid in self.stats.inserted_funding_ids:
                    try:
                        run_new_funding_alert_for(int(fid))
                    except Exception as exc:  # pragma: no cover
                        logger.warning(
                            f"[notif] new-funding alert failed for funding {fid}: {exc}"
                        )
            except Exception as exc:  # pragma: no cover
                logger.warning(f"[notif] new-funding alert hook failed: {exc}")
        return self.stats

    def expire_stale(self) -> int:
        """Mark ``is_active=False`` on rows whose deadline has lapsed."""
        now = datetime.utcnow()
        expired = (
            self.db.query(Funding)
            .filter(Funding.is_active == True)  # noqa: E712
            .filter(Funding.application_deadline.isnot(None))
            .filter(Funding.application_deadline < now)
            .all()
        )
        count = 0
        for f in expired:
            f.is_active = False
            count += 1
        if count:
            self._commit()
            self.stats.expired += count
        return count

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _ingest_one(self, raw: NormalizedFunding) -> None:
        try:
            record = validate_normalized(raw)
        except ValidationError as exc:
            self.stats.skipped += 1
            self._record_error("validate", getattr(raw, "source_id", None), str(exc))
            return

        # Look up existing (source, source_id) row first.
        existing_source = (
            self.db.query(FundingSource)
            .filter(FundingSource.source == record.source)
            .filter(FundingSource.source_id == record.source_id)
            .first()
        )

        if existing_source is not None:
            self._update_existing(existing_source, record)
            return

        # Cross-provider dedup: same opportunity published by a second source?
        merged_with_existing = self._find_cross_provider_duplicate(record)
        if merged_with_existing is not None:
            self._merge_into_existing(merged_with_existing, record)
            return

        self._insert_new(record)

    def _insert_new(self, record: NormalizedFunding) -> None:
        funding = self._to_funding_row(record)
        funding.is_active = compute_status(record.deadline, record.status) != "closed"
        self.db.add(funding)
        self.db.flush()  # need funding.id

        src = FundingSource(
            funding_id=funding.id,
            source=record.source,
            source_id=record.source_id,
            source_url=record.source_url,
            last_synced_at=datetime.utcnow(),
        )
        self.db.add(src)
        self.stats.inserted += 1
        # Track for the post-commit notification hook.  The hook runs
        # from ``ingest_batch`` after ``_commit()`` succeeds so the
        # funding row is fully visible to downstream readers.
        self.stats.inserted_funding_ids.append(int(funding.id))

    def _update_existing(self, source_row: FundingSource, record: NormalizedFunding) -> None:
        funding = self.db.query(Funding).filter(Funding.id == source_row.funding_id).first()
        if funding is None:
            # Orphan source row — promote to new insert.
            self._insert_new(record)
            return

        before = self._snapshot(funding)
        self._apply_to_funding(funding, record)
        self._apply_to_source(source_row, record)
        after = self._snapshot(funding)

        if before != after:
            self.stats.updated += 1
        else:
            self.stats.skipped += 1

    def _find_cross_provider_duplicate(self, record: NormalizedFunding) -> Optional[Funding]:
        """Return an existing funding row that looks like the same opportunity.

        The candidate filter previously used a Python ``or`` chained to
        ``Funding.organization == record.organization or Funding.organization
        == record.agency`` — but SQLAlchemy's ``filter`` only accepts the
        *last* expression, and the Python chained ``or`` short-circuits
        the whole thing to a single boolean. We now use ``or_()`` so each
        comparison is actually ORed in SQL.
        """
        query = self.db.query(Funding).filter(Funding.id.isnot(None))
        conditions = []
        if record.organization:
            conditions.append(Funding.organization == record.organization)
        if record.agency:
            conditions.append(Funding.organization == record.agency)
        if record.title:
            # Same canonical title from a previous ingest (deduped at the
            # DB layer) is also a candidate.
            conditions.append(Funding.title == record.title)
        if conditions:
            query = query.filter(or_(*conditions))
        # Cap the candidate pool to a reasonable scan size.
        candidates = query.order_by(Funding.created_at.desc()).limit(500).all()

        for cand in candidates:
            # Skip records already mapped to the same provider.
            if any(s.source == record.source for s in cand.sources):
                continue
            if is_duplicate(
                record,
                existing_title=cand.title,
                existing_agency=cand.organization or "",
                existing_deadline=cand.application_deadline,
            ):
                return cand
        return None

    def _merge_into_existing(self, existing: Funding, incoming: NormalizedFunding) -> None:
        # Build a synthetic canonical record from the existing row + incoming
        # so we reuse the merge helper.

        # Helper: build a topical ``research_area`` for the canonical record
        # from the existing row, treating each dedicated column as its own
        # value rather than collapsing them onto ``research_domain``.
        canonical_research_area = (
            getattr(existing, "research_area", None)
            or getattr(existing, "research_domain", None)
        )
        canonical_category = getattr(existing, "category", None)

        canonical = NormalizedFunding(
            source="existing",
            source_id=str(existing.id),
            title=existing.title,
            description=existing.description,
            agency=getattr(existing, "agency", None) or existing.organization,
            organization=existing.organization,
            country=existing.country,
            category=canonical_category,
            keywords=existing.keywords,
            research_area=canonical_research_area,
            funding_type=existing.funding_type,
            eligibility=existing.eligibility,
            funding_amount=existing.amount_max,
            currency=existing.currency,
            minimum_amount=existing.amount_min,
            maximum_amount=existing.amount_max,
            deadline=existing.application_deadline,
            posted_date=getattr(existing, "posted_date", None) or existing.created_at,
            status=(getattr(existing, "status", None)
                    or ("open" if existing.is_active else "closed")),
            source_url=existing.url,
            last_updated=existing.updated_at,
            extra_metadata=dict(existing.extra_metadata or {}),
        )
        merged = merge_normalized(canonical=canonical, incoming=incoming)
        self._apply_to_funding(existing, merged)
        existing.is_active = compute_status(merged.deadline, merged.status) != "closed"

        # Add the new FundingSource pointing at the existing row.
        if not any(s.source == incoming.source for s in existing.sources):
            self.db.add(
                FundingSource(
                    funding_id=existing.id,
                    source=incoming.source,
                    source_id=incoming.source_id,
                    source_url=incoming.source_url,
                    last_synced_at=datetime.utcnow(),
                )
            )
        self.stats.duplicates += 1
        self.stats.updated += 1

    # ------------------------------------------------------------------
    # Mapping helpers
    # ------------------------------------------------------------------
    def _to_funding_row(self, record: NormalizedFunding) -> Funding:
        return Funding(
            title=record.title,
            description=record.description,
            summary=(record.description or "")[:_SUMMARY_MAX],
            keywords=record.keywords,
            research_area=record.research_area,
            category=record.category,
            agency=record.agency,
            # research_domain is the legacy broad-field column. Use the
            # incoming topical classification if provided so the corpus
            # doesn't carry two parallel fields of the same value.
            research_domain=record.research_area or record.category,
            organization=record.organization or record.agency,
            sponsor=record.organization or record.agency,
            country=record.country,
            funding_type=record.funding_type,
            amount_min=record.minimum_amount,
            amount_max=record.maximum_amount,
            currency=record.currency or "USD",
            application_deadline=record.deadline,
            posted_date=record.posted_date,
            status=record.status,
            eligibility=record.eligibility,
            url=record.source_url,
            source=record.source,
            is_active=True,
            extra_metadata={
                **(record.extra_metadata or {}),
                "funding_intel": {
                    "source": record.source,
                    "source_id": record.source_id,
                    "posted_date": record.posted_date.isoformat() if record.posted_date else None,
                    "last_updated": record.last_updated.isoformat() if record.last_updated else None,
                    "status": record.status,
                },
            },
        )

    def _apply_to_funding(self, funding: Funding, record: NormalizedFunding) -> None:
        # Only overwrite fields when the new value is non-null. This
        # preserves manual data and keeps the merge idempotent.
        def set_if(field_name: str, value):
            if value in (None, "", []):
                return
            setattr(funding, field_name, value)

        set_if("title", record.title)
        set_if("description", record.description)
        set_if("summary", (record.description or "")[:_SUMMARY_MAX])
        set_if("keywords", record.keywords)
        set_if("research_area", record.research_area)
        set_if("category", record.category)
        set_if("agency", record.agency)
        # research_domain is the broad-field column: only overwrite if it
        # is currently empty, OR if the incoming value has topical
        # information (research_area / category) that the existing row
        # lacks.
        if record.research_area or record.category:
            set_if("research_domain", record.research_area or record.category)
        else:
            set_if("research_domain", None)
        set_if("organization", record.organization or record.agency)
        set_if("sponsor", record.organization or record.agency)
        set_if("country", record.country)
        set_if("funding_type", record.funding_type)
        set_if("amount_min", record.minimum_amount)
        set_if("amount_max", record.maximum_amount)
        set_if("currency", record.currency)
        set_if("application_deadline", record.deadline)
        set_if("posted_date", record.posted_date)
        set_if("status", record.status)
        set_if("eligibility", record.eligibility)
        set_if("url", record.source_url)
        set_if("source", record.source)

        existing_meta = dict(funding.extra_metadata or {})
        fi_meta = dict((existing_meta.get("funding_intel") or {}))
        fi_meta.update({
            "source": record.source,
            "source_id": record.source_id,
            "posted_date": record.posted_date.isoformat() if record.posted_date else None,
            "last_updated": record.last_updated.isoformat() if record.last_updated else None,
            "status": record.status,
        })
        existing_meta["funding_intel"] = fi_meta
        existing_meta.update(record.extra_metadata or {})
        funding.extra_metadata = existing_meta

    def _apply_to_source(self, source_row: FundingSource, record: NormalizedFunding) -> None:
        source_row.source_url = record.source_url or source_row.source_url
        source_row.last_synced_at = datetime.utcnow()

    def _record_error(self, kind: str, source_id: Optional[str], message: str) -> None:
        self.db.add(
            SyncRunError(
                run_id=self.run.id,
                provider=self.run.provider,
                source_id=source_id,
                error_type=kind,
                error_message=message[:2000],
            )
        )

    def _commit(self) -> None:
        try:
            self.db.commit()
        except Exception as exc:
            self.db.rollback()
            logger.error(f"[{self.run.provider}] ingest commit failed: {exc}")
            self.stats.errors.append(f"commit failed: {exc}")

    @staticmethod
    def _snapshot(funding: Funding) -> Dict:
        return {
            "title": funding.title,
            "description": funding.description,
            "summary": funding.summary,
            "organization": funding.organization,
            "sponsor": getattr(funding, "sponsor", None),
            "country": funding.country,
            "funding_type": funding.funding_type,
            "amount_min": funding.amount_min,
            "amount_max": funding.amount_max,
            "currency": funding.currency,
            "application_deadline": funding.application_deadline,
            "posted_date": getattr(funding, "posted_date", None),
            "status": getattr(funding, "status", None),
            "eligibility": funding.eligibility,
            "url": funding.url,
            "research_domain": funding.research_domain,
            "research_area": getattr(funding, "research_area", None),
            "category": getattr(funding, "category", None),
            "agency": getattr(funding, "agency", None),
            "source": getattr(funding, "source", None),
            "keywords": funding.keywords,
        }


__all__ = ["IngestService", "IngestStats", "title_similarity"]
