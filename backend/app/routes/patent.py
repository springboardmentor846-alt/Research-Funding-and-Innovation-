from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.patent import Patent
from app.schemas.patent import PatentCreate
from sqlalchemy import func

router = APIRouter(tags=["Patent"])


@router.post("/patents")
def add_patent(
    patent: PatentCreate,
    db: Session = Depends(get_db)
):

    new_patent = Patent(
        title=patent.title,
        assignee=patent.assignee,
        filing_date=patent.filing_date,
        patent_classification=patent.patent_classification,
        technology_domain=patent.technology_domain,
        citation_count=patent.citation_count
    )

    db.add(new_patent)
    db.commit()
    db.refresh(new_patent)

    return {
        "message": "Patent Added Successfully",
        "patent_id": new_patent.id
    }
@router.get("/patents")
def get_all_patents(
    db: Session = Depends(get_db)
):

    patents = db.query(Patent).all()

    return patents

@router.get("/patents/search/{technology_domain}")
def search_patents(
    technology_domain: str,
    db: Session = Depends(get_db)
):

    patents = db.query(Patent).filter(
        Patent.technology_domain.ilike(f"%{technology_domain}%")
    ).all()

    return patents

@router.get("/patents/clusters")
def patent_clusters(
    db: Session = Depends(get_db)
):

    clusters = (
        db.query(
            Patent.technology_domain,
            func.count(Patent.id).label("total_patents")
        )
        .group_by(Patent.technology_domain)
        .all()
    )

    return [
        {
            "Technology Domain": domain,
            "Patent Count": count
        }
        for domain, count in clusters
    ]

@router.get("/patents/trends")
def patent_trends(
    db: Session = Depends(get_db)
):

    trends = (
        db.query(
            Patent.filing_date,
            func.count(Patent.id).label("total")
        )
        .group_by(Patent.filing_date)
        .order_by(Patent.filing_date)
        .all()
    )

    return [
        {
            "Filing Date": date,
            "Patents Filed": total
        }
        for date, total in trends
    ]

@router.get("/patents/competitor/{assignee}")
def competitor_patents(
    assignee: str,
    db: Session = Depends(get_db)
):

    patents = db.query(Patent).filter(
        Patent.assignee.ilike(f"%{assignee}%")
    ).all()

    return {
        "Competitor": assignee,
        "Patent Count": len(patents),
        "Patents": patents
    }

@router.get("/patents/innovation-map")
def innovation_map(
    db: Session = Depends(get_db)
):

    patents = db.query(Patent).all()

    mapping = {}

    for patent in patents:
        domain = patent.technology_domain

        if domain not in mapping:
            mapping[domain] = []

        mapping[domain].append({
            "Patent": patent.title,
            "Assignee": patent.assignee,
            "Citations": patent.citation_count
        })

    return mapping

@router.get("/patents/analytics")
def patent_analytics(
    db: Session = Depends(get_db)
):

    total_patents = db.query(Patent).count()

    total_citations = db.query(
        func.sum(Patent.citation_count)
    ).scalar()

    average_citations = db.query(
        func.avg(Patent.citation_count)
    ).scalar()

    top_patent = db.query(Patent).order_by(
        Patent.citation_count.desc()
    ).first()

    return {
        "Total Patents": total_patents,
        "Total Citations": total_citations or 0,
        "Average Citations": round(average_citations or 0, 2),
        "Top Patent": top_patent
    }