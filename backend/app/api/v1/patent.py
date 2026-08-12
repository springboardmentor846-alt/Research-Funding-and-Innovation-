"""
Patent Landscape & Intellectual Property Analytics API Endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies.db import get_db
from app.models.patent import Patent
from app.schemas.patent import PatentResponse, PatentLandscapeAnalytics
from app.services.patent_service import PatentService

patent_router = APIRouter(prefix="/patents", tags=["Patent Landscape & IP Analytics"])


@patent_router.get("/landscape", response_model=PatentLandscapeAnalytics)
async def get_patent_landscape_analytics(db: AsyncSession = Depends(get_db)):
    service = PatentService(db)
    return await service.get_landscape_analytics()


@patent_router.get("/search", response_model=List[PatentResponse])
async def search_patents(
    query: Optional[str] = Query(None, description="Search by title, assignee, or classification"),
    assignee: Optional[str] = Query(None),
    ipc_code: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Patent)
    if ipc_code:
        stmt = stmt.where(Patent.ipc_classification == ipc_code)
    
    result = await db.execute(stmt.order_by(Patent.citation_count.desc()))
    patents = result.scalars().all()

    if assignee:
        patents = [p for p in patents if assignee.lower() in p.assignee.lower()]

    if query:
        q_lower = query.lower()
        patents = [
            p for p in patents 
            if q_lower in p.title.lower() 
            or q_lower in p.assignee.lower() 
            or q_lower in p.technology_domain.lower()
            or q_lower in p.ipc_classification.lower()
        ]

    return patents
