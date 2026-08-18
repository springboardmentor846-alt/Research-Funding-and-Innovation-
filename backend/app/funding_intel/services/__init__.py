"""Funding Intelligence services.

- ``sync``    : orchestrator that wires providers -> ingest -> DB.
- ``ingest``  : persistence helpers for ``NormalizedFunding`` records.
"""
from .sync import SyncEngine, ProviderReport
from .ingest import IngestService, IngestStats

__all__ = [
    "SyncEngine",
    "ProviderReport",
    "IngestService",
    "IngestStats",
]
