from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import CommercializationOpportunity
from app.schemas.schemas import CommercializationRead, CommercializationCreate
from typing import List, Optional

router = APIRouter(prefix="/commercialization", tags=["Commercialization Module"])

@router.get("", response_model=List[CommercializationRead])
def list_commercialization_opportunities(
    insight_type: Optional[str] = None,
    industry: Optional[str] = None,
    db: Session = Depends(get_db)
):
    q = db.query(CommercializationOpportunity)
    if insight_type and insight_type != "All":
        q = q.filter(CommercializationOpportunity.insight_type.ilike(f"%{insight_type}%"))
    if industry and industry != "All":
        q = q.filter(CommercializationOpportunity.target_industry.ilike(f"%{industry}%"))
    return q.all()

@router.post("", response_model=CommercializationRead, status_code=status.HTTP_201_CREATED)
def create_commercialization_opportunity(
    opp_in: CommercializationCreate,
    db: Session = Depends(get_db)
):
    opp = CommercializationOpportunity(**opp_in.model_dump())
    db.add(opp)
    db.commit()
    db.refresh(opp)
    return opp
