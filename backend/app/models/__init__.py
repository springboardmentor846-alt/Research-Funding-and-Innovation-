"""
SQLAlchemy models initialization.
"""
from app.models.user import User, RefreshToken, UserRole
from app.models.research_profile import (
    ResearchProfile,
    Publication,
    Patent,
    ResearchProject,
    OrganizationType,
    PatentStatus,
    ProjectStatus,
)
from app.models.funding import (
    FundingOpportunity,
    FundingBookmark,
    FundingAlert,
)
from app.models.research_intelligence import (
    ResearchPaper,
    ResearchTrend,
)
from app.models.patent import (
    PatentRecord,
    PatentTrend,
)
from app.models.technology import (
    TechnologyTrend,
    InnovationScore,
)
from app.models.commercialization import (
    CommercializationOpportunity,
    IndustryPartner,
    StartupRecommendation,
    Collaboration,
)
from app.models.reports_notifications import (
    Notification,
    Report,
)

__all__ = [
    "User",
    "RefreshToken",
    "UserRole",
    "ResearchProfile",
    "Publication",
    "Patent",
    "ResearchProject",
    "OrganizationType",
    "PatentStatus",
    "ProjectStatus",
    "FundingOpportunity",
    "FundingBookmark",
    "FundingAlert",
    "ResearchPaper",
    "ResearchTrend",
    "PatentRecord",
    "PatentTrend",
    "TechnologyTrend",
    "InnovationScore",
    "CommercializationOpportunity",
    "IndustryPartner",
    "StartupRecommendation",
    "Collaboration",
    "Notification",
    "Report",
]
