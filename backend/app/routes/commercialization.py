from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db

from app.auth import verify_token

from app.models.user import User

from app.models.commercialization import Commercialization

from app.schemas.commercialization import CommercializationCreate

router = APIRouter(
    tags=["Commercialization"]
)

@router.post("/commercialization")
def commercialization_analysis(
    data: CommercializationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):

    user = db.query(User).filter(
        User.email == current_user["sub"]
    ).first()

    if not user:
        return {"message": "User not found"}

    if data.innovation_score >= 80:
        product = "Suitable for commercial product development"
    else:
        product = "Needs further research"

    if data.patent_strength >= 70:
        licensing = "Strong candidate for licensing"
    else:
        licensing = "Patent portfolio should be strengthened"

    if (
        data.market_potential >= 80
        and data.technology_maturity >= 6
    ):
        startup = "High startup creation potential"
    else:
        startup = "Startup creation not yet recommended"

    if data.market_potential >= 70:
        partnership = "Suitable for industry collaboration"
    else:
        partnership = "Academic partnerships recommended"

    score = (
        data.innovation_score * 0.4 +
        data.market_potential * 0.3 +
        data.patent_strength * 0.3
    )

    record = Commercialization(
        researcher_email=user.email,
        technology_name=data.technology_name,
        product_recommendation=product,
        licensing_recommendation=licensing,
        startup_recommendation=startup,
        partnership_recommendation=partnership,
        commercialization_score=round(score, 2)
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "message": "Commercialization analysis completed",
        "Commercialization Score": record.commercialization_score,
        "Product Recommendation": product,
        "Licensing": licensing,
        "Startup": startup,
        "Partnership": partnership
    }

@router.get("/commercialization")
def get_all_commercialization(
    db: Session = Depends(get_db)
):

    records = db.query(Commercialization).all()

    return records

@router.get("/commercialization/productization")
def productization_recommendations(
    db: Session = Depends(get_db)
):

    recommendations = db.query(Commercialization).all()

    return [
        {
            "Technology": r.technology_name,
            "Recommendation": r.product_recommendation
        }
        for r in recommendations
    ]

@router.get("/commercialization/licensing")
def licensing_recommendations(
    db: Session = Depends(get_db)
):

    recommendations = db.query(Commercialization).all()

    return [
        {
            "Technology": r.technology_name,
            "Licensing": r.licensing_recommendation
        }
        for r in recommendations
    ]

@router.get("/commercialization/startup")
def startup_recommendations(
    db: Session = Depends(get_db)
):

    recommendations = db.query(Commercialization).all()

    return [
        {
            "Technology": r.technology_name,
            "Startup Recommendation": r.startup_recommendation
        }
        for r in recommendations
    ]

@router.get("/commercialization/partnership")
def partnership_recommendations(
    db: Session = Depends(get_db)
):

    recommendations = db.query(Commercialization).all()

    return [
        {
            "Technology": r.technology_name,
            "Partnership": r.partnership_recommendation
        }
        for r in recommendations
    ]

@router.get("/commercialization/dashboard")
def commercialization_dashboard(
    db: Session = Depends(get_db)
):

    total = db.query(Commercialization).count()

    average = db.query(
        func.avg(Commercialization.commercialization_score)
    ).scalar()

    highest = db.query(Commercialization).order_by(
        Commercialization.commercialization_score.desc()
    ).first()

    return {
        "Total Commercialization Assessments": total,
        "Average Score": round(average or 0, 2),
        "Highest Score": highest.commercialization_score if highest else 0,
        "Top Technology": highest.technology_name if highest else None,
        "Top Researcher": highest.researcher_email if highest else None
    }