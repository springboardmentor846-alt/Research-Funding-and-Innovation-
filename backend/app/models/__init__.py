"""Database models package."""
from app.models.user import User  # noqa: F401
from app.models.publication import Publication  # noqa: F401
from app.models.funding import Funding  # noqa: F401
from app.models.recommendation import Recommendation  # noqa: F401
from app.models.collaboration import Collaboration  # noqa: F401
from app.models.funding_history import FundingHistory  # noqa: F401
from app.models.research_interest import ResearchInterest  # noqa: F401
from app.models.saved_patent import SavedPatent  # noqa: F401
from app.models.notification import Notification, AlertPreference  # noqa: F401

# Funding Intelligence Service: provider-keyed identity + sync bookkeeping.
# These models are imported for their side-effect of registering with
# ``Base.metadata`` so ``init_db()`` creates the tables.
from app.funding_intel.models import (  # noqa: F401,E402
    FundingSource,
    SyncRun,
    SyncRunError,
    SyncControl,
)

# Patent Analytics & Innovation Intelligence (Milestone 3): the content
# tables (patents, patent_clusters, innovation_scores, technology_trends,
# patent_dashboard_cache) plus the operational tables (patent_sync_runs,
# patent_sync_run_errors, patent_sync_control) so ``init_db`` creates
# every table on a fresh database.
from app.patents.models import (  # noqa: F401,E402
    PatentSyncRun,
    PatentSyncRunError,
    PatentSyncControl,
)
