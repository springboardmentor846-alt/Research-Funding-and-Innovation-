"""External patent data providers.

Each provider is fully isolated:
- Owns its own HTTP client (via ``PatentProviderHTTPClient``).
- Owns its own request shape, error handling, and pagination.
- Translates raw upstream records into the unified
  ``NormalizedPatent`` model.
- Never raises to the caller during ``fetch_batch``/``normalize``;
  errors are recorded against its ``PatentProviderHealth`` snapshot.

The order of provider classes in this file is the order they are
registered with the registry.  Importing this module is what
triggers registration.

Note: Google Patents and USPTO are kept in the registry for backward
compatibility but are **disabled by default** — the Lens Patent API is
the sole data source for the patent analytics module.
"""
from .google_patents import GooglePatentsProvider
from .uspto import USPTOProvider
from .the_lens import TheLensProvider

__all__ = [
    "GooglePatentsProvider",
    "USPTOProvider",
    "TheLensProvider",
]
