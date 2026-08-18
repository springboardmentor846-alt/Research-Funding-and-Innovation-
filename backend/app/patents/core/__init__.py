"""Core primitives for the Patent Intelligence Service.

Mirrors the layout of ``app/funding_intel/core`` so the two services
feel like siblings.  Anything provider-agnostic lives here.
"""
from .base import BasePatentProvider, NormalizedPatent, PatentProviderHealth
from .config import patent_intel_settings, provider_flags
from .registry import (
    register_patent_provider,
    all_patent_providers,
    get_patent_provider,
    known_patent_providers,
    enabled_patent_provider_names,
)

__all__ = [
    "BasePatentProvider",
    "NormalizedPatent",
    "PatentProviderHealth",
    "patent_intel_settings",
    "provider_flags",
    "register_patent_provider",
    "all_patent_providers",
    "get_patent_provider",
    "known_patent_providers",
    "enabled_patent_provider_names",
]
