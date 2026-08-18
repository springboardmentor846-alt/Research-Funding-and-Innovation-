"""Funding Intelligence Service: shared configuration and contracts."""
from .config import FundingIntelSettings, funding_intel_settings
from .base import BaseProvider, ProviderError, ProviderHealth, NormalizedFunding

__all__ = [
    "FundingIntelSettings",
    "funding_intel_settings",
    "BaseProvider",
    "ProviderError",
    "ProviderHealth",
    "NormalizedFunding",
]
