from app.models.research_profile import ResearchProfile


def calculate_match(profile, funding):

    score = 0

    reasons = []

    # Research Domain

    if profile.research_domain.lower() == funding.research_domain.lower():

        score += 40

        reasons.append("Research Domain Matched")

    # Technology Area

    if profile.technology_area.lower() in funding.description.lower():

        score += 20

        reasons.append("Technology Area Matched")

    # Organization

    if profile.organization.lower() in funding.eligibility.lower():

        score += 15

        reasons.append("Organization Eligible")

    # Publications

    if profile.publications >= 5:

        score += 15

        reasons.append("Publication Requirement Satisfied")

    # Experience

    if profile.experience >= 3:

        score += 10

        reasons.append("Experience Requirement Satisfied")

    return {

        "funding_title": funding.title,

        "agency": funding.funding_agency,

        "match_score": score,

        "eligibility": "Eligible" if score >= 60 else "Needs Review",

        "reasons": reasons,

        "deadline": funding.deadline,

        "amount": funding.funding_amount

    }