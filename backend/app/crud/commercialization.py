from sqlalchemy.orm import Session

from app.crud.innovation import get_innovation_score
from app.crud.technology import get_technology_intelligence


def get_commercialization_recommendations(db: Session, profile):
    score_data = get_innovation_score(db, profile)
    breakdown = score_data["breakdown"]
    tech_data = get_technology_intelligence(db, top_n=20)

    research_novelty = breakdown["research_novelty"]["score"]
    patent_strength = breakdown["patent_strength"]["score"]
    tech_maturity = breakdown["technology_maturity"]["score"]
    market_potential = breakdown["market_potential"]["score"]

    recommendations = []

    if research_novelty >= 40 and patent_strength < 40:
        recommendations.append({
            "type": "Productization",
            "recommendation": "Your research shows strong novelty but limited patent coverage. "
                               "Consider developing a prototype or MVP to move your findings toward "
                               "a marketable product.",
            "priority": "High" if research_novelty >= 70 else "Medium",
        })

    if patent_strength >= 40 and tech_maturity >= 40:
        recommendations.append({
            "type": "Licensing Opportunity",
            "recommendation": "Your patent portfolio combined with mature technology areas suggests "
                               "strong licensing potential. Consider approaching industry players for "
                               "licensing agreements.",
            "priority": "High" if patent_strength >= 70 else "Medium",
        })

    if market_potential >= 40 and score_data["innovation_score"] >= 40:
        recommendations.append({
            "type": "Startup Creation",
            "recommendation": "Strong market alignment and overall innovation potential indicate this "
                               "could be a viable foundation for a startup venture.",
            "priority": "High" if score_data["innovation_score"] >= 60 else "Medium",
        })

    cross_domain_techs = [t["technology"] for t in tech_data if t.get("cross_domain")]
    if cross_domain_techs:
        top_examples = ", ".join(cross_domain_techs[:3])
        recommendations.append({
            "type": "Industry Partnership",
            "recommendation": f"Technologies like {top_examples} appear in both your research and "
                               f"patents, signaling strong industry relevance. Explore partnerships "
                               f"with companies active in these areas.",
            "priority": "Medium",
        })

    if not recommendations:
        recommendations.append({
            "type": "Getting Started",
            "recommendation": "Add more publications and patents to your profile to unlock "
                               "personalized commercialization recommendations.",
            "priority": "Low",
        })

    return recommendations