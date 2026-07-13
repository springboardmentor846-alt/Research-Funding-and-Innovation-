from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from sqlalchemy import func

from app.auth import verify_token

from app.models.user import User

from app.models.innovation_score import InnovationScore

from app.schemas.innovation_score import InnovationScoreCreate

router = APIRouter(
    tags=["Innovation Scoring"]
)

@router.post("/innovation-score")
def calculate_innovation_score(
    innovation: InnovationScoreCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):

    user = db.query(User).filter(
        User.email == current_user["sub"]
    ).first()

    score = (
        innovation.research_novelty * 0.30 +
        innovation.patent_strength * 0.20 +
        innovation.technology_maturity * 0.15 +
        innovation.market_potential * 0.20 +
        innovation.funding_relevance * 0.15
    )

    if score >= 85:
        level = "Excellent"
    elif score >= 70:
        level = "High"
    elif score >= 55:
        level = "Medium"
    else:
        level = "Low"

    record = InnovationScore(
        researcher_email=user.email,
        research_novelty=innovation.research_novelty,
        patent_strength=innovation.patent_strength,
        technology_maturity=innovation.technology_maturity,
        market_potential=innovation.market_potential,
        funding_relevance=innovation.funding_relevance,
        innovation_score=round(score, 2),
        innovation_level=level
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "Innovation Score": record.innovation_score,
        "Innovation Level": record.innovation_level
    }

@router.get("/innovation-score/research-impact")
def research_impact(
    db: Session = Depends(get_db)
):

    scores = db.query(InnovationScore).all()

    result = []

    for score in scores:

        if score.research_novelty >= 85:
            impact = "Excellent"

        elif score.research_novelty >= 70:
            impact = "High"

        elif score.research_novelty >= 55:
            impact = "Medium"

        else:
            impact = "Low"

        result.append({
            "Researcher": score.researcher_email,
            "Research Novelty": score.research_novelty,
            "Impact": impact
        })

    return result

@router.get("/innovation-score/technology-readiness")
def technology_readiness(
    db: Session = Depends(get_db)
):

    scores = db.query(InnovationScore).all()

    result = []

    for score in scores:

        if score.technology_maturity >= 85:
            readiness = "TRL High"

        elif score.technology_maturity >= 70:
            readiness = "TRL Medium"

        else:
            readiness = "TRL Low"

        result.append({
            "Researcher": score.researcher_email,
            "Technology Maturity": score.technology_maturity,
            "Readiness": readiness
        })

    return result

@router.get("/innovation-score/commercial-viability")
def commercial_viability(
    db: Session = Depends(get_db)
):

    scores = db.query(InnovationScore).all()

    result = []

    for score in scores:

        if score.market_potential >= 85:
            viability = "Excellent"

        elif score.market_potential >= 70:
            viability = "Good"

        else:
            viability = "Low"

        result.append({
            "Researcher": score.researcher_email,
            "Market Potential": score.market_potential,
            "Commercial Viability": viability
        })

    return result

@router.get("/innovation-score/funding-attractiveness")
def funding_attractiveness(
    db: Session = Depends(get_db)
):

    scores = db.query(InnovationScore).all()

    result = []

    for score in scores:

        if score.funding_relevance >= 85:
            funding = "Highly Attractive"

        elif score.funding_relevance >= 70:
            funding = "Attractive"

        else:
            funding = "Needs Improvement"

        result.append({
            "Researcher": score.researcher_email,
            "Funding Relevance": score.funding_relevance,
            "Funding Attractiveness": funding
        })

    return result

@router.get("/innovation-score/dashboard")
def innovation_dashboard(
    db: Session = Depends(get_db)
):

    total = db.query(InnovationScore).count()

    avg_score = db.query(
        func.avg(InnovationScore.innovation_score)
    ).scalar()

    highest = db.query(InnovationScore).order_by(
        InnovationScore.innovation_score.desc()
    ).first()

    return {
        "Total Assessments": total,
        "Average Innovation Score": round(avg_score or 0, 2),
        "Highest Innovation Score": highest.innovation_score if highest else 0,
        "Top Researcher": highest.researcher_email if highest else None
    }