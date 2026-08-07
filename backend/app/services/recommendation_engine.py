from app.models.research_profile import ResearchProfile
from app.models.funding import FundingOpportunity


def generate_recommendations(profile: ResearchProfile, funding_list):

    recommendations = []

    for funding in funding_list:

        score = 0

        # Domain Matching
        if (
            funding.research_domain.lower()
            ==
            profile.research_domain.lower()
        ):
            score += 40

        # Technology Area Matching
        if (
            profile.technology_area.lower()
            in
            funding.description.lower()
        ):
            score += 25

        # Organization Eligibility
        if (
            profile.organization.lower()
            in
            funding.eligibility.lower()
        ):
            score += 20

        # Publications
        if profile.publications >= 5:
            score += 10

        # Experience
        if profile.experience >= 3:
            score += 5

        recommendations.append({

            "id": funding.id,

            "title": funding.title,

            "agency": funding.funding_agency,

            "amount": funding.funding_amount,

            "deadline": funding.deadline,

            "match_score": score,

            "description": funding.description

        })

    recommendations.sort(
        key=lambda x: x["match_score"],
        reverse=True
    )

    return recommendations