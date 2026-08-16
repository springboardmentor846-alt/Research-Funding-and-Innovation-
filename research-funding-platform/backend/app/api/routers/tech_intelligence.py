from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import TechTrend
from app.schemas.schemas import TechTrendRead, TechTrendCreate
from typing import List, Optional

router = APIRouter(prefix="/tech-intelligence", tags=["Technology Intelligence"])

@router.get("/trends", response_model=List[TechTrendRead])
def get_tech_trends(
    category: Optional[str] = None,
    stage: Optional[str] = None,
    db: Session = Depends(get_db)
):
    q = db.query(TechTrend)
    if category and category != "All":
        q = q.filter(TechTrend.category.ilike(f"%{category}%"))
    if stage and stage != "All":
        q = q.filter(TechTrend.adoption_stage.ilike(f"%{stage}%"))
    return q.all()

@router.get("/radar")
def get_tech_radar_data(db: Session = Depends(get_db)):
    trends = db.query(TechTrend).all()
    radar = []
    for t in trends:
        radar.append({
            "name": t.technology_name,
            "category": t.category,
            "trl": t.readiness_level,
            "growth": f"{t.growth_rate}%",
            "stage": t.adoption_stage,
            "market": t.market_size_est
        })
    return radar

@router.post("/trends", response_model=TechTrendRead, status_code=status.HTTP_201_CREATED)
def create_tech_trend(trend_in: TechTrendCreate, db: Session = Depends(get_db)):
    trend = TechTrend(**trend_in.model_dump())
    db.add(trend)
    db.commit()
    db.refresh(trend)
    return trend
