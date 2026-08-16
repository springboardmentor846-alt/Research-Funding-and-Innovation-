from sqlalchemy.orm import Session
from app.models.funding import FundingOpportunity
from app.schemas.funding import FundingCreate

import requests as http_requests


def create_funding(db: Session, data: FundingCreate):
    new_funding = FundingOpportunity(
        title=data.title,
        source=data.source,
        description=data.description,
        eligibility=data.eligibility,
        domains=data.domains,
        deadline=data.deadline,
        amount=data.amount,
        link=data.link,
    )
    db.add(new_funding)
    db.commit()
    db.refresh(new_funding)
    return new_funding


def get_all_funding(db: Session):
    return db.query(FundingOpportunity).all()


def get_funding_by_id(db: Session, funding_id: int):
    return db.query(FundingOpportunity).filter(FundingOpportunity.id == funding_id).first()


def search_funding(db: Session, keyword: str):
    """
    Search funding opportunities by keyword across title, domains, and description.
    """
    if not keyword or not keyword.strip():
        return db.query(FundingOpportunity).all()

    term = f"%{keyword.strip()}%"
    return (
        db.query(FundingOpportunity)
        .filter(
            (FundingOpportunity.title.ilike(term))
            | (FundingOpportunity.domains.ilike(term))
            | (FundingOpportunity.description.ilike(term))
        )
        .all()
    )


def get_recommended_funding(db: Session, user_domains: str, user_role: str = None):
    if not user_domains:
        return []

    user_keywords = [kw.strip().lower() for kw in user_domains.split(",") if kw.strip()]
    all_funding = db.query(FundingOpportunity).all()

    matched = []
    for funding in all_funding:
        if not funding.domains:
            continue
        funding_keywords = [kw.strip().lower() for kw in funding.domains.split(",") if kw.strip()]

        domain_match = False
        for uk in user_keywords:
            for fk in funding_keywords:
                if uk == fk or uk in fk or fk in uk:
                    domain_match = True
                    break
            if domain_match:
                break

        if not domain_match:
            continue

        if user_role and funding.eligibility:
            eligibility_text = funding.eligibility.lower()
            role_readable = user_role.replace("_", " ").lower()
            if role_readable not in eligibility_text and "all" not in eligibility_text:
                continue

        matched.append(funding)

    return matched


from app.core.cache import ttl_cache


@ttl_cache(seconds=300)
def search_grants_gov(keyword: str, limit: int = 10):
    """
    Live search against the Grants.gov public search2 API for real
    U.S. federal grant opportunities matching the given keyword.
    """
    try:
        response = http_requests.post(
            "https://api.grants.gov/v1/api/search2",
            json={"keyword": keyword, "rows": limit},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        hits = data.get("data", {}).get("oppHits", [])
    except Exception:
        return []

    results = []
    for hit in hits:
        results.append({
            "title": hit.get("title", "Untitled Opportunity"),
            "source": hit.get("agencyName", "Grants.gov"),
            "description": f"Opportunity number: {hit.get('number', 'N/A')}",
            "eligibility": "See Grants.gov for eligibility details",
            "domains": keyword,
            "deadline": hit.get("closeDate", "Not specified"),
            "amount": "See Grants.gov for details",
            "link": f"https://www.grants.gov/search-results-detail/{hit.get('id', '')}",
        })

    return results