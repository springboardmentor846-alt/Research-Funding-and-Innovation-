from sqlalchemy.orm import Session

from app.models.patent import Patent
from app.models.technology import Technology
from app.models.research_profile import ResearchProfile


def commercialization_analysis(db: Session):

    patent = db.query(Patent).first()
    technology = db.query(Technology).first()
    profile = db.query(ResearchProfile).first()

    if not patent or not technology or not profile:
        return None

    # -------------------------------
    # Innovation Score
    # -------------------------------
    innovation_score = (
        (patent.citation_count * 0.4)
        + (technology.growth_score * 0.35)
        + (technology.adoption_rate * 0.25)
    )

    innovation_score = round(min(innovation_score, 100), 2)

    # -------------------------------
    # Commercialization Readiness
    # -------------------------------
    if innovation_score >= 85:
        readiness = "High"
        startup = "Excellent"
        action = "Startup Incubation"
        funding = "DST SERB Research Grant"
        market = "Very High"
        risk = "Low"

    elif innovation_score >= 70:
        readiness = "Good"
        startup = "High"
        action = "Patent Licensing"
        funding = "BIRAC Innovation Grant"
        market = "High"
        risk = "Medium"

    elif innovation_score >= 50:
        readiness = "Moderate"
        startup = "Medium"
        action = "Industry Collaboration"
        funding = "AICTE Research Funding"
        market = "Moderate"
        risk = "Medium"

    else:
        readiness = "Low"
        startup = "Low"
        action = "Continue Research"
        funding = "University Seed Fund"
        market = "Low"
        risk = "High"

    return {
        "patent_title": patent.patent_title,
        "technology_name": technology.technology_name,
        "innovation_score": innovation_score,
        "commercialization_readiness": readiness,
        "startup_potential": startup,
        "recommended_action": action,
        "recommended_funding": funding,
        "target_industry": technology.category,
        "estimated_market_potential": market,
        "risk_level": risk
    }