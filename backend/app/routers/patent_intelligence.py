from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app import models

router = APIRouter(
    prefix="/patent-intelligence",
    tags=["Patent Intelligence"]
)


@router.get("/search")
def search_patents(
    keyword: str = "",
    db: Session = Depends(get_db)
):
    patents = db.query(models.Patent)

    if keyword:
        patents = patents.filter(
            models.Patent.title.ilike(f"%{keyword}%")
            |
            models.Patent.technology_domain.ilike(f"%{keyword}%")
            |
            models.Patent.assignee.ilike(f"%{keyword}%")
        )

    return patents.all()


@router.get("/technology-distribution")
def technology_distribution(
    db: Session = Depends(get_db)
):

    result = (
        db.query(
            models.Patent.technology_domain,
            func.count(models.Patent.id).label("count")
        )
        .group_by(models.Patent.technology_domain)
        .all()
    )

    return [
        {
            "technology": domain,
            "count": count
        }
        for domain, count in result
    ]


@router.get("/top-organizations")
def top_organizations(
    db: Session = Depends(get_db)
):

    result = (
        db.query(
            models.Patent.assignee,
            func.count(models.Patent.id).label("count")
        )
        .group_by(models.Patent.assignee)
        .order_by(func.count(models.Patent.id).desc())
        .limit(10)
        .all()
    )

    return [
        {
            "organization": org,
            "count": count
        }
        for org, count in result
    ]


@router.get("/innovation-map")
def innovation_map(
    db: Session = Depends(get_db)
):

    patents = db.query(models.Patent).all()

    return [
        {
            "title": patent.title,
            "technology": patent.technology_domain,
            "organization": patent.assignee,
            "filing_date": patent.filing_date
        }
        for patent in patents
    ]