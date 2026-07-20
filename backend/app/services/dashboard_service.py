from sqlalchemy import select

from app.models.publication import Publication
from app.models.patent import Patent
from app.models.funding import FundingOpportunity

from app.services.innovation_service import (
    calculate_innovation_score,
)


def calculate_profile_completion(profile):

    total_fields = 5
    completed_fields = 0

    if profile.bio:
        completed_fields += 1

    if profile.highest_qualification:
        completed_fields += 1

    if profile.current_position:
        completed_fields += 1

    if profile.organization_name:
        completed_fields += 1

    if profile.orcid_id:
        completed_fields += 1

    return round(
        (completed_fields / total_fields) * 100
    )


def get_dashboard_statistics(db, profile):

    # Statistics
    publication_count = db.query(Publication).filter(
        Publication.research_profile_id == profile.id
    ).count()

    patent_count = db.query(Patent).filter(
        Patent.research_profile_id == profile.id
    ).count()

    funding_count = db.query(
        FundingOpportunity
    ).count()

    # Latest Publications
    latest_publications = db.scalars(
        select(Publication)
        .where(
            Publication.research_profile_id == profile.id
        )
        .order_by(Publication.created_at.desc())
        .limit(5)
    ).all()

    # Latest Patents
    latest_patents = db.scalars(
        select(Patent)
        .where(
            Patent.research_profile_id == profile.id
        )
        .order_by(Patent.created_at.desc())
        .limit(5)
    ).all()

    # Innovation Score
    innovation = calculate_innovation_score(
        db,
        profile
    )

    # Profile Completion
    profile_completion = calculate_profile_completion(
        profile
    )

    return {

        "statistics": {
            "publications": publication_count,
            "patents": patent_count,
            "funding_opportunities": funding_count
        },

        "profile_completion": profile_completion,

        "innovation": innovation,

        "latest_publications": [
            {
                "title": publication.title,
                "publisher": publication.publisher,
                "doi": publication.doi
            }
            for publication in latest_publications
        ],

        "latest_patents": [
            {
                "title": patent.title,
                "status": patent.status,
                "patent_office": patent.patent_office
            }
            for patent in latest_patents
        ]
    }