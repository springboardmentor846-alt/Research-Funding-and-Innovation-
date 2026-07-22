from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.research_profile import ResearchProfile
from app.models.research_domain import ResearchDomain
from app.models.research_keyword import ResearchKeyword
from app.models.technology_area import TechnologyArea
from app.models.funding_opportunity import FundingOpportunity

from app.services.ai_service import calculate_similarity


def build_researcher_text(
    profile,
    domains,
    keywords,
    technologies
):
    parts = []

    if profile.bio:
        parts.append(profile.bio)

    if profile.highest_qualification:
        parts.append(profile.highest_qualification)

    if profile.current_position:
        parts.append(profile.current_position)

    for domain in domains:
        if domain.domain_name:
            parts.append(domain.domain_name)

    for keyword in keywords:
        if keyword.keyword:
            parts.append(keyword.keyword)

    for technology in technologies:
        if technology.technology_name:
            parts.append(technology.technology_name)

    return " ".join(parts)


def build_funding_text(funding):
    parts = []

    if funding.title:
        parts.append(funding.title)

    if funding.organization:
        parts.append(funding.organization)

    if funding.funding_type:
        parts.append(funding.funding_type)

    # Add these only if they exist in your FundingOpportunity model
    if getattr(funding, "description", None):
        parts.append(funding.description)

    if getattr(funding, "eligibility", None):
        parts.append(funding.eligibility)

    return " ".join(parts)


def recommend_funding(
    db: Session,
    user_id: int
):

    # --------------------------------
    # Get researcher profile
    # --------------------------------

    profile = db.scalar(
        select(ResearchProfile).where(
            ResearchProfile.user_id == user_id
        )
    )

    if profile is None:
        return []


    # --------------------------------
    # Get research domains
    # --------------------------------

    domains = db.scalars(
        select(ResearchDomain).where(
            ResearchDomain.research_profile_id == profile.id
        )
    ).all()


    # --------------------------------
    # Get research keywords
    # --------------------------------

    keywords = db.scalars(
        select(ResearchKeyword).where(
            ResearchKeyword.research_profile_id == profile.id
        )
    ).all()


    # --------------------------------
    # Get technology areas
    # --------------------------------

    technologies = db.scalars(
        select(TechnologyArea).where(
            TechnologyArea.research_profile_id == profile.id
        )
    ).all()


    # --------------------------------
    # Build researcher text
    # --------------------------------

    researcher_text = build_researcher_text(
        profile,
        domains,
        keywords,
        technologies
    )


    # --------------------------------
    # Get all funding opportunities
    # --------------------------------

    funding_opportunities = db.scalars(
        select(FundingOpportunity)
    ).all()


    recommendations = []


    # --------------------------------
    # Compare researcher with funding
    # --------------------------------

    for funding in funding_opportunities:

        funding_text = build_funding_text(
            funding
        )

        similarity = calculate_similarity(
            researcher_text,
            funding_text
        )

        relevance_percentage = round(
            similarity * 100,
            2
        )


        # --------------------------------
        # Relevance category
        # --------------------------------

        if relevance_percentage >= 70:
            relevance_level = "Highly Relevant"

        elif relevance_percentage >= 45:
            relevance_level = "Relevant"

        elif relevance_percentage >= 25:
            relevance_level = "Moderate Match"

        else:
            relevance_level = "Low Match"


        recommendations.append({

            "id": funding.id,

            "title": funding.title,

            "organization": funding.organization,

            "funding_type": funding.funding_type,

            "funding_amount": funding.funding_amount,

            "deadline": funding.deadline,

            "official_link": funding.official_link,

            "relevance_score":
                relevance_percentage,

            "relevance_level":
                relevance_level
        })


    # --------------------------------
    # Highest relevance first
    # --------------------------------

    recommendations.sort(
        key=lambda item:
            item["relevance_score"],
        reverse=True
    )


    return recommendations