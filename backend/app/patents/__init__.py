"""Patent Analytics & Innovation Intelligence module (Milestone 3).

Importing the submodules here registers the providers with the
registry, the SQLAlchemy models with ``Base.metadata``, and the
configuration with the rest of the platform.  Use the submodules
directly in code (e.g. ``from app.patents.core import ...``).
"""
from app.patents.core import (  # noqa: F401,E402
    patent_intel_settings,
    provider_flags,
    all_patent_providers,
    get_patent_provider,
    known_patent_providers,
    enabled_patent_provider_names,
)
from app.patents import models  # noqa: F401,E402
from app.patents.providers import (  # noqa: F401,E402
    GooglePatentsProvider,
    USPTOProvider,
    TheLensProvider,
)
