from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.technology import Technology
from app.schemas.technology import TechnologyCreate

router = APIRouter(tags=["Technology Intelligence"])


@router.post("/technology")
def add_technology(
    technology: TechnologyCreate,
    db: Session = Depends(get_db)
):

    new_technology = Technology(
    technology_name=technology.technology_name,
    domain=technology.domain,
    maturity_level=technology.maturity_level,
    trl_level=technology.trl_level,
    adoption_rate=technology.adoption_rate,
    opportunity_score=technology.opportunity_score,
    publication_count=technology.publication_count,
    patent_count=technology.patent_count,
    trend_score=technology.trend_score,
    competitor=technology.competitor,
    status=technology.status
    )

    db.add(new_technology)
    db.commit()
    db.refresh(new_technology)

    return {
        "message": "Technology Added Successfully",
        "technology_id": new_technology.id
    }

@router.get("/technology")
def get_all_technologies(
    db: Session = Depends(get_db)
):
    return db.query(Technology).all()

@router.get("/technology/emerging")
def emerging_technologies(
    db: Session = Depends(get_db)
):
    return db.query(Technology).filter(
        Technology.status == "Emerging"
    ).all()

@router.get("/technology/maturity")
def maturity_analysis(
    db: Session = Depends(get_db)
):
    return db.query(Technology).order_by(
        Technology.trl_level.desc()
    ).all()

@router.get("/technology/adoption")
def adoption_tracking(
    db: Session = Depends(get_db)
):
    return db.query(Technology).order_by(
        Technology.adoption_rate.desc()
    ).all()

@router.get("/technology/opportunities")
def innovation_opportunities(
    db: Session = Depends(get_db)
):
    return db.query(Technology).filter(
        Technology.opportunity_score >= 80
    ).all()

@router.get("/technology/competitors")
def competitors(
    db: Session = Depends(get_db)
):
    return db.query(Technology).all()

@router.get("/technology/dashboard")
def technology_dashboard(
    db: Session = Depends(get_db)
):

    total = db.query(Technology).count()

    avg_adoption = db.query(
        func.avg(Technology.adoption_rate)
    ).scalar()

    avg_opportunity = db.query(
        func.avg(Technology.opportunity_score)
    ).scalar()

    return {
        "Total Technologies": total,
        "Average Adoption Rate": round(avg_adoption or 0, 2),
        "Average Opportunity Score": round(avg_opportunity or 0, 2)
    }