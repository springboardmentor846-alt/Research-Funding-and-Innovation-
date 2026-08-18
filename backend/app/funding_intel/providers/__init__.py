"""External funding data providers.

Each provider is fully isolated:
- Owns its own HTTP client (via ``ProviderHTTPClient``).
- Owns its own request shape, error handling, and pagination.
- Translates raw upstream records into the unified
  ``NormalizedFunding`` model.
- Never raises to the caller during ``fetch_batch``/``normalize``;
  errors are recorded against its ``ProviderHealth`` snapshot.

The order of provider classes in this file is the order they are
registered with the provider registry. Importing this module is what
triggers registration.
"""
from .nih import NIHProvider
from .grants_gov import GrantsGovProvider
from .nsf import NSFProvider
from .openalex import OpenAlexProvider
from .cordis import CORDISProvider

__all__ = [
    "NIHProvider",
    "GrantsGovProvider",
    "NSFProvider",
    "OpenAlexProvider",
    "CORDISProvider",
]
