from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user
from app.services import research_trends_service

router = APIRouter()


@router.get("/overview")
def trends_overview(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """All trend charts in one call: publications by year, top domains,
    top keywords (word cloud), top technology areas."""
    return research_trends_service.trends_overview(db)


@router.get("/publications-by-year")
def publications_by_year(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return research_trends_service.publications_by_year(db)


@router.get("/top-domains")
def top_domains(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return research_trends_service.top_domains(db)


@router.get("/top-keywords")
def top_keywords(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return research_trends_service.top_keywords(db)


@router.get("/top-technology-areas")
def top_technology_areas(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return research_trends_service.top_technology_areas(db)