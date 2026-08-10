from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import crud

router = APIRouter(
    prefix="/innovation",
    tags=["Innovation Intelligence"]
)


@router.get("/score")
def innovation_score(
    db: Session = Depends(get_db)
):
    return crud.innovation_score(db)


@router.get("/portfolio-strength")
def portfolio_strength(
    db: Session = Depends(get_db)
):

    score = crud.innovation_score(db)

    if score["innovation_score"] >= 80:
        level = "Excellent"

    elif score["innovation_score"] >= 60:
        level = "Strong"

    elif score["innovation_score"] >= 40:
        level = "Moderate"

    else:
        level = "Developing"

    return {
        "portfolio_strength": level,
        "innovation_score": score["innovation_score"]
    }


@router.get("/innovation-index")
def innovation_index(
    db: Session = Depends(get_db)
):

    score = crud.innovation_score(db)

    publications = score["publications"]

    patents = score["patents"]

    index = round(
        (publications * 0.4) +
        (patents * 0.6),
        2
    )

    return {
        "innovation_index": index
    }


@router.get("/research-impact")
def research_impact(
    db: Session = Depends(get_db)
):

    score = crud.innovation_score(db)

    impact = round(
        score["innovation_score"] * 0.85,
        2
    )

    return {
        "research_impact": impact
    }