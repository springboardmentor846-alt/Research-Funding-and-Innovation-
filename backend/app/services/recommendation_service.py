from sqlalchemy.orm import Session
from app.models.funding import FundingOpportunity
from app.models.profile import ResearcherProfile
from app.models.publication import Publication
from typing import List, Dict


def _compute_score(profile: ResearcherProfile, pubs: List[Publication], funding: FundingOpportunity) -> Dict:
    """
    Compute a matching score between a researcher profile and a funding opportunity.
    Uses domain match, keyword overlap, and country/eligibility signals.
    """
    score = 0
    reasons = []

    # Domain match (40 points)
    profile_domain = (profile.research_domain or "").lower()
    funding_domain = (funding.research_domain or "").lower()
    if profile_domain and funding_domain:
        if profile_domain == funding_domain:
            score += 40
            reasons.append(f"Exact domain match: {funding.research_domain}")
        elif profile_domain in funding_domain or funding_domain in profile_domain:
            score += 25
            reasons.append(f"Partial domain match: {funding.research_domain}")

    # Keyword overlap (30 points)
    profile_keywords = set(
        kw.strip().lower() for kw in (profile.keywords or "").split(",") if kw.strip()
    )
    funding_text = (
        (funding.description or "") + " " + (funding.eligibility or "")
    ).lower()
    matched_keywords = [kw for kw in profile_keywords if kw in funding_text]
    if matched_keywords:
        kw_score = min(30, len(matched_keywords) * 10)
        score += kw_score
        reasons.append(f"Keyword matches: {', '.join(matched_keywords[:3])}")

    # Publication domain alignment (20 points)
    pub_domains = [p.research_domain.lower() for p in pubs if p.research_domain]
    if funding_domain and any(funding_domain in d or d in funding_domain for d in pub_domains):
        score += 20
        reasons.append("Publication history aligns with funding domain")

    # Organization/eligibility match (10 points)
    org = (profile.organization or "").lower()
    eligibility = (funding.eligibility or "").lower()
    if org and org in eligibility:
        score += 10
        reasons.append("Organization matches eligibility criteria")

    # Determine eligibility status
    if score >= 60:
        eligibility_status = "Eligible"
    elif score >= 30:
        eligibility_status = "Partially Eligible"
    else:
        eligibility_status = "Not Eligible"

    return {
        "funding_id": funding.id,
        "title": funding.title,
        "agency": funding.agency,
        "funding_amount": funding.funding_amount,
        "deadline": str(funding.deadline),
        "research_domain": funding.research_domain,
        "country": funding.country,
        "matching_score": score,
        "recommendation_percentage": min(100, score),
        "eligibility_status": eligibility_status,
        "reason": "; ".join(reasons) if reasons else "Low profile-funding alignment",
    }


def get_recommendations(db: Session, user_id: int) -> List[Dict]:
    """Return top 10 funding recommendations for a researcher."""
    profile = db.query(ResearcherProfile).filter(
        ResearcherProfile.user_id == user_id
    ).first()

    if not profile:
        return []

    publications = db.query(Publication).filter(
        Publication.organization == profile.organization
    ).all()

    all_funding = db.query(FundingOpportunity).filter(
        FundingOpportunity.status == "Open"
    ).all()

    scored = [_compute_score(profile, publications, f) for f in all_funding]
    scored.sort(key=lambda x: x["matching_score"], reverse=True)
    return scored[:10]
