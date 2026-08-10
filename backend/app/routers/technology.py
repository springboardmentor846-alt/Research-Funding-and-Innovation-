from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app import models

router = APIRouter(
    prefix="/technology",
    tags=["Technology Intelligence"]
)


@router.get("/emerging-technologies")
def emerging_technologies(
    db: Session = Depends(get_db)
):

    result = (
        db.query(
            models.Patent.technology_domain,
            func.count(models.Patent.id).label("count")
        )
        .group_by(models.Patent.technology_domain)
        .order_by(func.count(models.Patent.id).desc())
        .all()
    )

    return [
        {
            "technology": domain,
            "count": count
        }
        for domain, count in result
    ]


@router.get("/technology-maturity")
def technology_maturity(
    db: Session = Depends(get_db)
):

    patents = db.query(models.Patent).all()

    maturity = []

    for patent in patents:

        score = 25

        if patent.technology_domain:
            score += 35

        if patent.assignee:
            score += 20

        if patent.filing_date:
            score += 20

        maturity.append({
            "title": patent.title,
            "technology": patent.technology_domain,
            "maturity": score
        })

    return maturity


@router.get("/research-gap")
def research_gap(
    db: Session = Depends(get_db)
):

    patent_domains = {
        p.technology_domain.lower()
        for p in db.query(models.Patent).all()
    }

    funding_domains = {
        f.technology_area.lower()
        for f in db.query(models.FundingOpportunity).all()
    }

    gaps = list(funding_domains - patent_domains)

    return [
        {
            "technology": gap
        }
        for gap in gaps
    ]