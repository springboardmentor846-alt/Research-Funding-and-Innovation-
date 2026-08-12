"""
Research Profile Management API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.profile import ResearchProfile
from app.schemas.profile import ResearchProfileCreate, ResearchProfileUpdate, ResearchProfileResponse

profile_router = APIRouter(prefix="/profile", tags=["Research Profile Management"])


@profile_router.get("/me", response_model=ResearchProfileResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(ResearchProfile).where(ResearchProfile.user_id == current_user.id))
    profile = result.scalars().first()

    if not profile:
        # Auto-create blank research profile for user
        profile = ResearchProfile(
            user_id=current_user.id,
            organization="University / Organization",
            department="Research & Development",
            academic_title="Principal Investigator",
            bio="Research focus on AI, deep learning, and emerging innovation.",
            research_domains=["Artificial Intelligence", "Machine Learning"],
            keywords=["NLP", "Neural Networks", "Computer Vision"],
            technology_areas=["Deep Learning", "Automation"],
            total_publications=5,
            total_citations=120,
            h_index=4
        )
        db.add(profile)
        await db.commit()
        await db.refresh(profile)

    return profile


@profile_router.put("/me", response_model=ResearchProfileResponse)
async def update_my_profile(
    data: ResearchProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(ResearchProfile).where(ResearchProfile.user_id == current_user.id))
    profile = result.scalars().first()

    if not profile:
        profile = ResearchProfile(user_id=current_user.id)
        db.add(profile)

    for field, val in data.model_dump(exclude_unset=True).items():
        if val is not None:
            setattr(profile, field, val)

    await db.commit()
    await db.refresh(profile)
    return profile
