from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.database import get_db
from app.models.patent import Patent
from app.schemas.patent import (
    PatentCreate,
    PatentUpdate,
    PatentResponse,
)

router = APIRouter(
    prefix="/patents",
    tags=["Patent Intelligence"]
)


# ===========================
# Create Patent
# ===========================
@router.post("/", response_model=PatentResponse)
def create_patent(
    patent: PatentCreate,
    db: Session = Depends(get_db)
):
    new_patent = Patent(**patent.model_dump())

    db.add(new_patent)
    db.commit()
    db.refresh(new_patent)

    return new_patent


# ===========================
# Get All Patents
# ===========================
@router.get("/", response_model=list[PatentResponse])
def get_all_patents(
    db: Session = Depends(get_db)
):
    return db.query(Patent).all()


# ===========================
# Search by Technology Domain
# ===========================
@router.get("/search/domain", response_model=list[PatentResponse])
def search_by_domain(
    technology_domain: str,
    db: Session = Depends(get_db)
):
    patents = db.query(Patent).filter(
        Patent.technology_domain.ilike(f"%{technology_domain}%")
    ).all()

    return patents
# Search Patents by Assignee
@router.get("/search/assignee", response_model=list[PatentResponse])
def search_by_assignee(
    assignee: str,
    db: Session = Depends(get_db)
):
    patents = db.query(Patent).filter(
        Patent.assignee.ilike(f"%{assignee}%")
    ).all()

    return patents
# Patent Statistics
@router.get("/statistics")
def patent_statistics(
    db: Session = Depends(get_db)
):
    total = db.query(Patent).count()

    granted = db.query(Patent).filter(
        Patent.status == "Granted"
    ).count()

    pending = db.query(Patent).filter(
        Patent.status == "Pending"
    ).count()

    published = db.query(Patent).filter(
        Patent.status == "Published"
    ).count()

    return {
        "total_patents": total,
        "granted_patents": granted,
        "pending_patents": pending,
        "published_patents": published
    }
# Patent Domain Analytics
@router.get("/domain-summary")
def domain_summary(
    db: Session = Depends(get_db)
):
    results = (
        db.query(
            Patent.technology_domain,
            func.count(Patent.id).label("count")
        )
        .group_by(Patent.technology_domain)
        .all()
    )

    return [
        {
            "technology_domain": domain,
            "count": count
        }
        for domain, count in results
    ]
# ===========================
# Get Patent by ID
# ===========================
@router.get("/{patent_id}", response_model=PatentResponse)
def get_patent(
    patent_id: int,
    db: Session = Depends(get_db)
):
    patent = db.query(Patent).filter(
        Patent.id == patent_id
    ).first()

    if not patent:
        raise HTTPException(
            status_code=404,
            detail="Patent not found"
        )

    return patent


# ===========================
# Update Patent
# ===========================
@router.put("/{patent_id}", response_model=PatentResponse)
def update_patent(
    patent_id: int,
    updated_patent: PatentUpdate,
    db: Session = Depends(get_db)
):
    patent = db.query(Patent).filter(
        Patent.id == patent_id
    ).first()

    if not patent:
        raise HTTPException(
            status_code=404,
            detail="Patent not found"
        )

    for key, value in updated_patent.model_dump().items():
        setattr(patent, key, value)

    db.commit()
    db.refresh(patent)

    return patent


# ===========================
# Delete Patent
# ===========================
@router.delete("/{patent_id}")
def delete_patent(
    patent_id: int,
    db: Session = Depends(get_db)
):
    patent = db.query(Patent).filter(
        Patent.id == patent_id
    ).first()

    if not patent:
        raise HTTPException(
            status_code=404,
            detail="Patent not found"
        )

    db.delete(patent)
    db.commit()

    return {
        "message": "Patent deleted successfully"
    }