"""
Dashboard aggregation service.

Pulls together counts and summaries from across the platform's existing
tables (profile, publications, patents, funding, collaboration, startup)
into two views:

- get_user_dashboard(): a single researcher's own activity snapshot.
- get_platform_overview(): platform-wide numbers for Admin / Innovation
  Manager dashboards.

This module does not introduce any new tables — it only reads from models
that already exist, so it needs no migration.
"""
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.research_profile import ResearchProfile
from app.models.publication import Publication
from app.models.patent import Patent
from app.models.funding import FundingOpportunity
from app.models.startup import Startup
from app.models.collaboration_request import CollaborationRequest


def get_user_dashboard(db: Session, user_id: int) -> dict:
    """Aggregated snapshot for a single researcher's own dashboard."""
    profile = db.query(ResearchProfile).filter(ResearchProfile.user_id == user_id).first()

    publication_count = 0
    patent_count = 0
    if profile:
        publication_count = (
            db.query(Publication)
            .filter(Publication.profile_id == profile.id, Publication.source_type == "own")
            .count()
        )
        patent_count = db.query(Patent).filter(Patent.profile_id == profile.id).count()

    sent_requests = db.query(CollaborationRequest).filter(CollaborationRequest.sender_id == user_id)
    received_requests = db.query(CollaborationRequest).filter(CollaborationRequest.receiver_id == user_id)

    startup_profile = db.query(Startup).filter(Startup.user_id == user_id).first()

    return {
        "has_research_profile": profile is not None,
        "publication_count": publication_count,
        "patent_count": patent_count,
        "collaboration_requests": {
            "sent": sent_requests.count(),
            "received": received_requests.count(),
            "pending_received": received_requests.filter(CollaborationRequest.status == "pending").count(),
        },
        "has_startup_profile": startup_profile is not None,
        "startup_stage": startup_profile.stage if startup_profile else None,
        "funding_opportunities_available": db.query(FundingOpportunity).count(),
    }


def get_platform_overview(db: Session) -> dict:
    """Platform-wide numbers for Admin / Innovation Manager dashboards."""
    total_users = db.query(User).count()

    role_counts: dict[str, int] = {}
    for u in db.query(User).all():
        role_counts[u.role] = role_counts.get(u.role, 0) + 1

    total_startups = db.query(Startup).count()
    startups_by_stage: dict[str, int] = {}
    for s in db.query(Startup).all():
        startups_by_stage[s.stage] = startups_by_stage.get(s.stage, 0) + 1

    collaboration_by_status: dict[str, int] = {}
    for c in db.query(CollaborationRequest).all():
        collaboration_by_status[c.status] = collaboration_by_status.get(c.status, 0) + 1

    return {
        "total_users": total_users,
        "users_by_role": role_counts,
        "total_research_profiles": db.query(ResearchProfile).count(),
        "total_publications": db.query(Publication).count(),
        "total_patents": db.query(Patent).count(),
        "total_funding_opportunities": db.query(FundingOpportunity).count(),
        "total_startups": total_startups,
        "startups_by_stage": startups_by_stage,
        "collaboration_requests_by_status": collaboration_by_status,
    }