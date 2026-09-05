"""
Explanation service.

Mirrors the matching logic in app.crud.funding.get_recommended_funding,
but instead of just returning matched opportunities, it explains *why*
a given opportunity was (or wasn't) recommended for a profile — which
domain keywords overlapped, and whether the role/eligibility check passed.
This gives the researcher transparency into the recommendation instead
of a black-box list.
"""
from app.models.funding import FundingOpportunity


def explain_funding_match(user_domains: str, funding: FundingOpportunity, user_role: str = None):
    reasons = []
    matched_keywords = []

    user_keywords = [kw.strip().lower() for kw in (user_domains or "").split(",") if kw.strip()]
    funding_keywords = [kw.strip().lower() for kw in (funding.domains or "").split(",") if kw.strip()]

    for uk in user_keywords:
        for fk in funding_keywords:
            if uk == fk or uk in fk or fk in uk:
                matched_keywords.append(fk)
                break

    if matched_keywords:
        reasons.append(
            f"Your research domains overlap with this opportunity's focus areas: "
            f"{', '.join(sorted(set(matched_keywords)))}."
        )
    else:
        reasons.append("Your research domains do not overlap with this opportunity's focus areas.")

    role_ok = True
    if user_role and funding.eligibility:
        eligibility_text = funding.eligibility.lower()
        role_readable = user_role.replace("_", " ").lower()
        if role_readable not in eligibility_text and "all" not in eligibility_text:
            role_ok = False
            reasons.append(
                f"Your role ('{role_readable}') is not explicitly listed in this "
                f"opportunity's eligibility ('{funding.eligibility}')."
            )
        else:
            reasons.append(f"Your role ('{role_readable}') matches this opportunity's eligibility criteria.")

    is_match = bool(matched_keywords) and role_ok

    return {
        "funding_id": funding.id,
        "title": funding.title,
        "is_recommended": is_match,
        "matched_keywords": sorted(set(matched_keywords)),
        "reasons": reasons,
    }