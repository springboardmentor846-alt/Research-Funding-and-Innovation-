"""Normalization helpers for patent data ingested from heterogeneous sources.

Each provider (Google Patents, USPTO, The Lens) returns records in a
different shape.  ``normalize_patent_record`` converts any of those
shapes into a dict that maps 1:1 to ``PatentCreate`` (see
``app/schemas/patent.py``).  Down-stream ingestion is then purely a
matter of feeding the normalized dict into the repository.

The normalizer is intentionally defensive:

* It never raises on a missing field — the schema is permissive.
* It strips and lowercases identifiers so deduplication can key on
  ``patent_number`` reliably.
* It coerces dates via ``dateutil`` if available, otherwise the source
  must hand us ISO-8601.
* It derives ``publication_year`` from the publication date if
  missing.
* It derives a coarse ``technology_area`` from the CPC/IPC class
  prefix when the source did not supply one.
"""
from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List, Optional

try:  # python-dateutil is available in the project's requirements
    from dateutil import parser as _date_parser  # type: ignore
except Exception:  # pragma: no cover - extremely defensive
    _date_parser = None


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Allowed sources, in the same snake_case the rest of the platform uses.
ALLOWED_SOURCES = {"google_patents", "uspto", "the_lens"}

# Coarse IPC/CPC top-level prefixes -> technology_area label.  Used when
# the source did not supply a more specific bucket.  Keys are matched as
# prefixes against the normalized classification string.
_CPC_TECHNOLOGY_PREFIXES: List[tuple] = [
    ("A61", "Medical & Health"),
    ("A01", "Agriculture & Food"),
    ("A23", "Food Science"),
    ("B01", "Chemistry & Process Engineering"),
    ("B60", "Transportation"),
    ("B64", "Aerospace"),
    ("C01", "Industrial Chemistry"),
    ("C07", "Organic Chemistry"),
    ("C08", "Polymers & Materials"),
    ("C12", "Biotechnology"),
    ("C22", "Metallurgy"),
    ("E21", "Mining & Earth Sciences"),
    ("F03", "Engines & Pumps"),
    ("F16", "Mechanical Engineering"),
    ("F24", "Heating & Cooling"),
    ("G01", "Measurement & Instrumentation"),
    ("G02", "Optics & Photonics"),
    ("G06", "Computing & AI"),
    ("G06F", "Computing & AI"),
    ("G06N", "Computing & AI"),
    ("G10", "Acoustics & Music"),
    ("G11", "Information Storage"),
    ("H01", "Electronics & Semiconductors"),
    ("H01L", "Electronics & Semiconductors"),
    ("H02", "Electric Power"),
    ("H04", "Telecommunications"),
    ("H04L", "Telecommunications"),
    ("H04N", "Telecommunications"),
    ("H05", "Special Electric Tech"),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_PUNCT_RE = re.compile(r"[\s\-\._/]+")
_INVENTOR_SPLIT_RE = re.compile(r"\s*[,;|]\s*")


def normalize_patent_number(value: str) -> str:
    """Return a canonical patent number suitable for de-duplication.

    Strips whitespace and common separators, uppercases, and removes the
    country prefix when it appears in a known set.  The country code
    itself is *preserved* on the Patent row (it lives in ``country``).
    """
    if not value:
        return ""
    cleaned = _PUNCT_RE.sub("", value.strip()).upper()
    return cleaned


def split_inventors(value: Optional[str]) -> Optional[str]:
    """Normalize an inventor string into a canonical comma-separated form.

    Different sources use commas, semicolons, or pipes to separate
    inventor names.  ``Publication.normalize_inventors`` returns a
    canonical ``"Last, First; Last, First"`` string the rest of the
    platform can rely on.
    """
    if not value:
        return None
    parts = [p.strip() for p in _INVENTOR_SPLIT_RE.split(value) if p and p.strip()]
    if not parts:
        return None
    return ", ".join(parts)


def split_keywords(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    parts = [p.strip() for p in re.split(r"[,;|]", value) if p and p.strip()]
    if not parts:
        return None
    return ", ".join(parts)


def parse_date(value: Any) -> Optional[datetime]:
    """Parse a date value of arbitrary shape into a ``datetime``.

    Accepts: ``datetime``, ISO-8601 strings, common slashes, epoch
    seconds, ``None``.  Returns ``None`` on failure rather than raising.
    """
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, (int, float)):
        try:
            return datetime.utcfromtimestamp(float(value))
        except (OverflowError, OSError, ValueError):
            return None
    if isinstance(value, str):
        if _date_parser is not None:
            try:
                return _date_parser.parse(value)
            except (ValueError, TypeError, OverflowError):
                return None
        # Last-ditch ISO-8601 attempt
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None


def detect_technology_area(classification: Optional[str]) -> Optional[str]:
    """Map a CPC/IPC class to a coarse technology bucket.

    Returns ``None`` if the classification is empty or does not match
    any known prefix.
    """
    if not classification:
        return None
    code = classification.strip().upper()
    for prefix, label in _CPC_TECHNOLOGY_PREFIXES:
        if code.startswith(prefix):
            return label
    return None


def detect_country(patent_number: str) -> Optional[str]:
    """Best-effort country detection from a patent number prefix."""
    if not patent_number:
        return None
    pn = patent_number.upper()
    if pn.startswith("US"):
        return "US"
    if pn.startswith("EP"):
        return "EP"
    if pn.startswith("WO"):
        return "WO"
    if pn.startswith("JP"):
        return "JP"
    if pn.startswith("CN"):
        return "CN"
    if pn.startswith("KR"):
        return "KR"
    if pn.startswith("DE"):
        return "DE"
    if pn.startswith("GB"):
        return "GB"
    return None


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def normalize_patent_record(record: Dict[str, Any], *, source: str) -> Dict[str, Any]:
    """Coerce a raw provider payload into a dict suitable for ``PatentCreate``.

    Parameters
    ----------
    record:
        Raw record from a provider.  May use any of: ``patent_id`` /
        ``publication_number`` / ``id`` for the patent number, ``title``,
        ``abstract`` / ``summary``, ``inventors`` / ``inventor``,
        ``assignee`` / ``applicant``, ``filing_date`` / ``date``,
        ``publication_date`` / ``pub_date``, ``country``,
        ``classification`` / ``cpc`` / ``ipc``, ``citations`` /
        ``cited_by_count``, ``url`` / ``link``.
    source:
        One of ``"google_patents"``, ``"uspto"``, ``"the_lens"``.  Will
        be passed through unchanged and is required by the dedup
        key.
    """
    if source not in ALLOWED_SOURCES:
        raise ValueError(f"Unknown patent source: {source!r}")

    patent_number = (
        record.get("patent_number")
        or record.get("patent_id")
        or record.get("publication_number")
        or record.get("id")
        or record.get("lens_id")
        or ""
    )
    patent_number = normalize_patent_number(str(patent_number))

    title = (record.get("title") or "").strip()
    abstract = record.get("abstract") or record.get("summary") or None

    inventors_raw = record.get("inventors") or record.get("inventor")
    inventors = split_inventors(inventors_raw if isinstance(inventors_raw, str) else None)

    assignee = record.get("assignee") or record.get("applicant") or record.get("organization")
    if isinstance(assignee, list):
        assignee = ", ".join(str(a) for a in assignee if a)

    country = record.get("country") or detect_country(patent_number)

    classification = (
        record.get("classification")
        or record.get("cpc")
        or record.get("ipc")
        or record.get("ipc_class")
    )
    if isinstance(classification, list):
        classification = ", ".join(str(c) for c in classification if c)
    classification_label = record.get("classification_label") or record.get("cpc_label")

    filing_date = parse_date(record.get("filing_date") or record.get("date_filed"))
    publication_date = parse_date(
        record.get("publication_date") or record.get("pub_date") or record.get("date_published")
    )
    publication_year = (
        record.get("publication_year")
        or record.get("year")
        or (publication_date.year if publication_date else None)
    )

    citations = record.get("citations")
    if citations is None:
        citations = record.get("cited_by_count") or 0
    try:
        citations = int(citations or 0)
    except (TypeError, ValueError):
        citations = 0

    keywords_raw = record.get("keywords")
    keywords = split_keywords(keywords_raw if isinstance(keywords_raw, str) else None)

    technology_area = (
        record.get("technology_area")
        or record.get("technology")
        or record.get("category")
        or detect_technology_area(classification if isinstance(classification, str) else None)
    )

    url = record.get("url") or record.get("link")
    source_id = str(record.get("source_id") or record.get("id") or patent_number)

    legal_status = record.get("legal_status") or record.get("status")
    patent_family = record.get("patent_family") or record.get("family_id")

    out: Dict[str, Any] = {
        "patent_number": patent_number,
        "title": title,
        "abstract": abstract,
        "inventors": inventors,
        "assignee": assignee,
        "technology_area": technology_area,
        "keywords": keywords,
        "country": country,
        "classification": classification if isinstance(classification, str) else None,
        "classification_label": classification_label,
        "filing_date": filing_date,
        "publication_date": publication_date,
        "publication_year": publication_year,
        "citations": citations,
        "patent_family": patent_family,
        "legal_status": legal_status,
        "source": source,
        "source_id": source_id,
        "url": url,
    }

    # ------------------------------------------------------------------
    # Lens-specific columns
    # ------------------------------------------------------------------
    # The Lens provider stashes its bibliographic fields in
    # ``extra_metadata["_lens"]`` so the provider-agnostic
    # ``NormalizedPatent`` contract can stay narrow.  Here we lift them
    # onto the top-level dict so the SQLAlchemy ``Patent`` row gets
    # them populated on insert/update.  When the dict comes from an
    # older provider the values default to ``None``.
    lens_extra = (record.get("extra_metadata") or {}).get("_lens") or {}
    if source == "the_lens":
        # Required fields first.
        out["lens_id"] = lens_extra.get("lens_id") or record.get("lens_id")
        # Coerce back into proper Python types for SQLAlchemy.
        cpc = lens_extra.get("cpc_classifications")
        ipc = lens_extra.get("ipc_classifications")
        out["cpc_classifications"] = (
            list(cpc) if isinstance(cpc, list) else (cpc or None)
        )
        out["ipc_classifications"] = (
            list(ipc) if isinstance(ipc, list) else (ipc or None)
        )
        applicant_names = lens_extra.get("applicant_names")
        inventor_names = lens_extra.get("inventor_names")
        out["applicant_names"] = (
            list(applicant_names)
            if isinstance(applicant_names, list)
            else (applicant_names or None)
        )
        out["inventor_names"] = (
            list(inventor_names)
            if isinstance(inventor_names, list)
            else (inventor_names or None)
        )
        out["npl_citations_count"] = lens_extra.get("npl_citations_count")
        out["patent_citations_count"] = lens_extra.get("patent_citations_count")
        out["family_size"] = lens_extra.get("family_size")
        out["earliest_priority_date"] = parse_date(
            lens_extra.get("earliest_priority_date")
        )
        out["grant_date"] = parse_date(lens_extra.get("grant_date"))
        out["jurisdiction"] = lens_extra.get("jurisdiction") or country
        out["doc_type"] = lens_extra.get("doc_type")
        out["lens_url"] = lens_extra.get("lens_url") or url
        out["last_synced_at"] = record.get("last_synced_at") or datetime.utcnow()
        # Persist the original Lens metadata alongside the row.
        out["extra_metadata"] = {
            k: v
            for k, v in lens_extra.items()
            if k
            not in {
                # already lifted to top-level columns
                "lens_id",
                "ipc_classifications",
                "cpc_classifications",
                "npl_citations_count",
                "patent_citations_count",
                "family_size",
                "earliest_priority_date",
                "grant_date",
                "applicant_names",
                "inventor_names",
                "jurisdiction",
                "doc_type",
                "lens_url",
                # fields that already map onto standard columns above
                "kind",
            }
        }
    else:
        out["extra_metadata"] = record.get("extra_metadata") or {}
        out["last_synced_at"] = record.get("last_synced_at") or datetime.utcnow()

    return out
