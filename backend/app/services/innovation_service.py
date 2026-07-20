from sqlalchemy import select

from app.models.publication import Publication
from app.models.patent import Patent
from app.models.research_domain import ResearchDomain
from app.models.research_keyword import ResearchKeyword
from app.models.technology_area import TechnologyArea


def calculate_innovation_score(db, profile):

    publications = db.scalars(
        select(Publication).where(
            Publication.research_profile_id == profile.id
        )
    ).all()

    patents = db.scalars(
        select(Patent).where(
            Patent.research_profile_id == profile.id
        )
    ).all()

    domains = db.scalars(
        select(ResearchDomain).where(
            ResearchDomain.research_profile_id == profile.id
        )
    ).all()

    keywords = db.scalars(
        select(ResearchKeyword).where(
            ResearchKeyword.research_profile_id == profile.id
        )
    ).all()

    technologies = db.scalars(
        select(TechnologyArea).where(
            TechnologyArea.research_profile_id == profile.id
        )
    ).all()

    score = 0

    # Publications (30)
    score += min(len(publications) * 3, 30)

    # Patents (25)
    score += min(len(patents) * 5, 25)

    # Domains (10)
    score += min(len(domains) * 2, 10)

    # Keywords (10)
    score += min(len(keywords), 10)

    # Technology Areas (10)
    score += min(len(technologies) * 2, 10)

    # Profile Completeness (15)
    profile_score = 0

    if profile.bio:
        profile_score += 3

    if profile.highest_qualification:
        profile_score += 3

    if profile.current_position:
        profile_score += 3

    if profile.organization_name:
        profile_score += 3

    if profile.orcid_id:
        profile_score += 3

    score += profile_score

    score = min(score, 100)

    return {
        "innovation_score": score,
        "breakdown": {
            "publications": min(len(publications) * 3, 30),
            "patents": min(len(patents) * 5, 25),
            "domains": min(len(domains) * 2, 10),
            "keywords": min(len(keywords), 10),
            "technology_areas": min(len(technologies) * 2, 10),
            "profile": profile_score
        }
    }