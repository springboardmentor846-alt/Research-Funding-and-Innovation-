from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.research_trend import ResearchTrend
from app.schemas.research_trend import (
    ResearchTrendCreate,
    ResearchTrendResponse,
)

router = APIRouter(prefix="/trends", tags=["Research Trends"])


# Create Research Trend
@router.post("/", response_model=ResearchTrendResponse)
def create_trend(
    trend: ResearchTrendCreate,
    db: Session = Depends(get_db)
):
    new_trend = ResearchTrend(
        research_domain=trend.research_domain,
        year=trend.year,
        publications=trend.publications,
        trend_score=trend.trend_score,
    )

    db.add(new_trend)
    db.commit()
    db.refresh(new_trend)

    return new_trend


# Get All Trends
@router.get("/", response_model=list[ResearchTrendResponse])
def get_trends(db: Session = Depends(get_db)):
    return db.query(ResearchTrend).all()


# Get Trend by ID
@router.get("/{trend_id}", response_model=ResearchTrendResponse)
def get_trend(trend_id: int, db: Session = Depends(get_db)):
    trend = db.query(ResearchTrend).filter(
        ResearchTrend.id == trend_id
    ).first()

    if not trend:
        raise HTTPException(status_code=404, detail="Trend not found")

    return trend