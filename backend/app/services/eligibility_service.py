from sqlalchemy.orm import Session
from app.models.funding import FundingOpportunity
from app.models.profile import ResearcherProfile
from typing import Dict


def check_eligibility(db: Session, user_id: int, funding_id: int) -> Dict:
    """
    Compare researcher profile against a specific funding opportunity
    and return eligibility status with matching percentage.
    """
    profile = db.query(ResearcherProfile).filter(
        ResearcherProfile.user_id == user_id
    ).first()

    funding = db.query(FundingOpportunity).filter(
        FundingOpportunity.id == funding_id
    ).first()

    if not profile or not funding:
        return {"error": "Profile or funding opportunity not found"}

    criteria = []
    matched = 0

    # 1. Research Domain
    p_domain = (profile.research_domain or "").lower()
    f_domain = (funding.research_domain or "").lower()
    domain_match = p_domain == f_domain or p_domain in f_domain or f_domain in p_domain
    criteria.append({"criterion": "Research Domain", "matched": domain_match,
                     "profile_value": profile.research_domain,
                     "required_value": funding.research_domain})
    if domain_match:
        matched += 1

    # 2. Country (if funding restricts country)
    country_match = True  # default open
    criteria.append({"criterion": "Country", "matched": country_match,
                     "profile_value": "International",
                     "required_value": funding.country})

    # 3. Organization type
    org = (profile.organization or "").lower()
    eligibility_text = (funding.eligibility or "").lower()
    org_match = not eligibility_text or org in eligibility_text or "all" in eligibility_text
    criteria.append({"criterion": "Organization", "matched": org_match,
                     "profile_value": profile.organization,
                     "required_value": funding.eligibility[:80]})
    if org_match:
        matched += 1

    # 4. Keywords overlap
    profile_kws = set(k.strip().lower() for k in (profile.keywords or "").split(",") if k.strip())
    kw_match = any(kw in eligibility_text for kw in profile_kws)
    criteria.append({"criterion": "Keywords", "matched": kw_match,
                     "profile_value": profile.keywords,
                     "required_value": "Relevant research keywords"})
    if kw_match:
        matched += 1

    # 5. Experience (designation proxy)
    designation = (profile.designation or "").lower()
    exp_match = bool(designation)
    criteria.append({"criterion": "Experience/Designation", "matched": exp_match,
                     "profile_value": profile.designation,
                     "required_value": "Active researcher"})
    if exp_match:
        matched += 1

    total_criteria = len(criteria)
    match_percentage = round((matched / total_criteria) * 100)

    if match_percentage >= 70:
        status = "Eligible"
    elif match_percentage >= 40:
        status = "Partially Eligible"
    else:
        status = "Not Eligible"

    return {
        "funding_id": funding_id,
        "funding_title": funding.title,
        "agency": funding.agency,
        "funding_amount": funding.funding_amount,
        "status": status,
        "match_percentage": match_percentage,
        "criteria": criteria,
    }
