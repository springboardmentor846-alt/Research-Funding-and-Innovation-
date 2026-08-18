"""Funding Intelligence Service.

A self-contained, provider-agnostic funding ingestion layer that
automates the discovery, normalization, deduplication, validation,
synchronization, and observability of research-funding opportunities.

Public surface
--------------
- `app.funding_intel.providers`     : One adapter per external data source.
- `app.funding_intel.core`          : Base contracts, configuration, registry.
- `app.funding_intel.schemas`       : Pydantic unified funding schema.
- `app.funding_intel.quality`       : Validation, deduplication, expiration.
- `app.funding_intel.services`      : High-level orchestrators (sync, ingest).
- `app.funding_intel.scheduler`     : Background jobs.
- `app.funding_intel.api`           : FastAPI admin router.

The existing `app.models.funding.Funding` SQLAlchemy model is reused as
the canonical store. The new `FundingSource` table records the
provider-keyed identity of each ingested record so that subsequent
syncs can upsert in place.
"""

# Import provider modules eagerly so the registry is populated before the
# sync engine resolves provider names during startup or API calls.
from app.funding_intel import providers as _providers  # noqa: F401

__all__ = ["providers"]
