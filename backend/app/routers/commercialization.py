from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import crud

router = APIRouter(
    prefix="/commercialization",
    tags=["Commercialization"]
)


@router.get("/recommendations")
def commercialization_recommendations(
    db: Session = Depends(get_db)
):

    score = crud.innovation_score(db)

    recommendations = []

    if score["patents"] >= 5:
        recommendations.append({
            "type": "Patent Licensing",
            "description": "Commercialize patents through licensing."
        })

    if score["publications"] >= 5:
        recommendations.append({
            "type": "Industry Collaboration",
            "description": "Partner with industries for technology transfer."
        })

    if (
        score["patents"] >= 3 and
        score["publications"] >= 3
    ):
        recommendations.append({
            "type": "Startup Opportunity",
            "description": "Innovation portfolio is suitable for startup creation."
        })

    if score["innovation_score"] >= 70:
        recommendations.append({
            "type": "Government Grant",
            "description": "Eligible for commercialization funding."
        })

    if len(recommendations) == 0:
        recommendations.append({
            "type": "Research Improvement",
            "description": "Increase patents and publications for better commercialization opportunities."
        })

    return recommendations


@router.get("/licensing")
def licensing(
    db: Session = Depends(get_db)
):

    score = crud.innovation_score(db)

    return {
        "eligible": score["patents"] >= 3,
        "patents": score["patents"]
    }


@router.get("/startup")
def startup(
    db: Session = Depends(get_db)
):

    score = crud.innovation_score(db)

    return {
        "recommended": (
            score["patents"] >= 3 and
            score["publications"] >= 3
        ),
        "innovation_score": score["innovation_score"]
    }


@router.get("/industry")
def industry(
    db: Session = Depends(get_db)
):

    score = crud.innovation_score(db)

    return {
        "recommended": score["publications"] >= 5,
        "publications": score["publications"]
    }