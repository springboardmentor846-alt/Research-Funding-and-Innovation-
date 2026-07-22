from sqlalchemy.orm import Session

from app.models.patent import Patent
from app.models.technology import Technology
from app.models.research_profile import ResearchProfile


def calculate_innovation(db: Session):

    patent = db.query(Patent).first()
    technology = db.query(Technology).first()
    profile = db.query(ResearchProfile).first()

    if not patent or not technology or not profile:
        return None

    # -----------------------------
    # Innovation Score Calculation
    # -----------------------------
    score = (
        (patent.citation_count * 0.4)
        + (technology.growth_score * 0.35)
        + (technology.adoption_rate * 0.25)
    )

    score = round(min(score, 100), 2)

    # -----------------------------
    # Innovation Level
    # -----------------------------
    if score >= 85:
        level = "Excellent"
    elif score >= 70:
        level = "High"
    elif score >= 50:
        level = "Moderate"
    else:
        level = "Low"

    # -----------------------------
    # Commercialization Probability
    # -----------------------------
    if score >= 80:
        probability = "High"
    elif score >= 60:
        probability = "Medium"
    else:
        probability = "Low"

    # -----------------------------
    # Recommendation
    # -----------------------------
    if score >= 85:
        recommendation = (
            "Strong candidate for startup incubation and patent commercialization."
        )
    elif score >= 70:
        recommendation = (
            "Recommended for industry collaboration and grant funding."
        )
    elif score >= 50:
        recommendation = (
            "Needs further research and prototype validation."
        )
    else:
        recommendation = (
            "Requires significant improvement before commercialization."
        )

    return {
        "patent_title": patent.patent_title,
        "technology_name": technology.technology_name,
        "research_domain": profile.research_domain,
        "innovation_score": score,
        "innovation_level": level,
        "commercialization_probability": probability,
        "recommendation": recommendation,
    }