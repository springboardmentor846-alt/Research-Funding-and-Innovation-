from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Patent
from app.schemas.schemas import PatentRead, PatentCreate
from typing import List, Optional

router = APIRouter(prefix="/patent-intelligence", tags=["Patent Intelligence"])

@router.get("/patents", response_model=List[PatentRead])
def list_patents(
    query: Optional[str] = None,
    tech_field: Optional[str] = None,
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    q = db.query(Patent)
    if query:
        search_pattern = f"%{query}%"
        q = q.filter(
            (Patent.title.ilike(search_pattern)) |
            (Patent.assignee.ilike(search_pattern)) |
            (Patent.patent_number.ilike(search_pattern)) |
            (Patent.abstract.ilike(search_pattern))
        )
    if tech_field and tech_field != "All":
        q = q.filter(Patent.tech_field.ilike(f"%{tech_field}%"))
    if status_filter and status_filter != "All":
        q = q.filter(Patent.status == status_filter)

    return q.offset(skip).limit(limit).all()

@router.get("/analytics")
def get_patent_analytics(db: Session = Depends(get_db)):
    patents = db.query(Patent).all()
    total_patents = len(patents)
    active_patents = sum(1 for p in patents if p.status == "Active")
    pending_patents = sum(1 for p in patents if p.status == "Pending")

    assignees = {}
    tech_clusters = {}
    for p in patents:
        assignees[p.assignee] = assignees.get(p.assignee, 0) + 1
        tech_clusters[p.tech_field] = tech_clusters.get(p.tech_field, 0) + 1

    top_assignees = sorted([{"assignee": k, "count": v} for k, v in assignees.items()], key=lambda x: x["count"], reverse=True)[:5]
    top_fields = sorted([{"field": k, "count": v} for k, v in tech_clusters.items()], key=lambda x: x["count"], reverse=True)[:5]

    return {
        "total_patents": total_patents,
        "active_patents": active_patents,
        "pending_patents": pending_patents,
        "top_assignees": top_assignees,
        "top_fields": top_fields
    }

@router.post("/patents", response_model=PatentRead, status_code=status.HTTP_201_CREATED)
def create_patent(patent_in: PatentCreate, db: Session = Depends(get_db)):
    existing = db.query(Patent).filter(Patent.patent_number == patent_in.patent_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Patent with this number already exists.")
    
    p = Patent(**patent_in.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p
