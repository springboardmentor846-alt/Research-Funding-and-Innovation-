from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import InnovationScore
from app.schemas.schemas import InnovationScoreRead, InnovationScoreCalculate
from app.services.scoring_engine import scoring_engine
from typing import List

router = APIRouter(prefix="/innovation-score", tags=["Innovation Scoring Engine"])

@router.get("", response_model=List[InnovationScoreRead])
def list_innovation_scores(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return db.query(InnovationScore).order_by(InnovationScore.overall_score.desc()).offset(skip).limit(limit).all()

@router.post("/calculate", response_model=InnovationScoreRead)
def calculate_and_save_score(payload: InnovationScoreCalculate, db: Session = Depends(get_db)):
    calc = scoring_engine.calculate_score(
        novelty=payload.novelty_score,
        patent_strength=payload.patent_strength,
        tech_maturity=payload.tech_maturity,
        market_potential=payload.market_potential,
        funding_relevance=payload.funding_relevance
    )

    score_record = InnovationScore(
        entity_type=payload.entity_type,
        entity_name=payload.entity_name,
        novelty_score=calc["novelty_score"],
        patent_strength=calc["patent_strength"],
        tech_maturity=calc["tech_maturity"],
        market_potential=calc["market_potential"],
        funding_relevance=calc["funding_relevance"],
        overall_score=calc["overall_score"],
        recommendations=calc["recommendations"]
    )
    db.add(score_record)
    db.commit()
    db.refresh(score_record)
    return score_record
