"""
API Endpoints for Research Profile Management, Publications, Patents, Projects, and Search.
"""
import uuid
from typing import List, Optional
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.research_profile import (
    ResearchProfileResponse,
    ResearchProfileUpdate,
    PublicationCreate,
    PublicationUpdate,
    PublicationResponse,
    PatentCreate,
    PatentUpdate,
    PatentResponse,
    ResearchProjectCreate,
    ResearchProjectUpdate,
    ResearchProjectResponse,
    ResearcherSearchResult,
)
from app.services.research_profile_service import ResearchProfileService

router = APIRouter(prefix="/research-profile", tags=["Research Profile Management"])


def _map_profile_response(profile) -> ResearchProfileResponse:
    return ResearchProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        full_name=profile.user.full_name if profile.user else None,
        user_email=profile.user.email if profile.user else None,
        user_role=profile.user.role.value if profile.user else None,
        organization_name=profile.organization_name,
        department=profile.department,
        organization_type=profile.organization_type,
        position=profile.position,
        academic_degree=profile.academic_degree,
        field_of_study=profile.field_of_study,
        institution_name=profile.institution_name,
        graduation_year=profile.graduation_year,
        h_index=profile.h_index or 0,
        i10_index=profile.i10_index or 0,
        total_citations=profile.total_citations or 0,
        orcid_id=profile.orcid_id,
        google_scholar_url=profile.google_scholar_url,
        scopus_id=profile.scopus_id,
        research_domains=profile.research_domains or [],
        keywords=profile.keywords or [],
        technology_interests=profile.technology_interests or [],
        summary_bio=profile.summary_bio,
        avatar_url=profile.avatar_url,
        publications=[
            PublicationResponse.model_validate(p) for p in profile.publications
        ],
        patents=[PatentResponse.model_validate(p) for p in profile.patents],
        projects=[ResearchProjectResponse.model_validate(p) for p in profile.projects],
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


# ── Profile endpoints ─────────────────────────────────────────────────────────
@router.get(
    "/me",
    response_model=ResearchProfileResponse,
    summary="Get current user's research profile",
)
async def get_my_research_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await ResearchProfileService.get_or_create_profile(db, current_user.id)
    return _map_profile_response(profile)


@router.put(
    "/me",
    response_model=ResearchProfileResponse,
    summary="Update current user's research profile",
)
async def update_my_research_profile(
    data: ResearchProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await ResearchProfileService.update_profile(db, current_user.id, data)
    return _map_profile_response(profile)


@router.post(
    "/me/avatar",
    summary="Upload profile picture / avatar",
)
async def upload_profile_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    avatar_url = await ResearchProfileService.upload_avatar(db, current_user.id, file)
    return {"message": "Avatar uploaded successfully", "avatar_url": avatar_url}


# ── Publications endpoints ───────────────────────────────────────────────────
@router.post(
    "/me/publications",
    response_model=PublicationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a publication",
)
async def add_publication(
    data: PublicationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    pub = await ResearchProfileService.add_publication(db, current_user.id, data)
    return PublicationResponse.model_validate(pub)


@router.put(
    "/me/publications/{pub_id}",
    response_model=PublicationResponse,
    summary="Update a publication",
)
async def update_publication(
    pub_id: uuid.UUID,
    data: PublicationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    pub = await ResearchProfileService.update_publication(
        db, current_user.id, pub_id, data
    )
    return PublicationResponse.model_validate(pub)


@router.delete(
    "/me/publications/{pub_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a publication",
)
async def delete_publication(
    pub_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await ResearchProfileService.delete_publication(db, current_user.id, pub_id)


# ── Patents endpoints ─────────────────────────────────────────────────────────
@router.post(
    "/me/patents",
    response_model=PatentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a patent",
)
async def add_patent(
    data: PatentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    pat = await ResearchProfileService.add_patent(db, current_user.id, data)
    return PatentResponse.model_validate(pat)


@router.put(
    "/me/patents/{pat_id}",
    response_model=PatentResponse,
    summary="Update a patent",
)
async def update_patent(
    pat_id: uuid.UUID,
    data: PatentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    pat = await ResearchProfileService.update_patent(
        db, current_user.id, pat_id, data
    )
    return PatentResponse.model_validate(pat)


@router.delete(
    "/me/patents/{pat_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a patent",
)
async def delete_patent(
    pat_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await ResearchProfileService.delete_patent(db, current_user.id, pat_id)


# ── Research Projects endpoints ───────────────────────────────────────────────
@router.post(
    "/me/projects",
    response_model=ResearchProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a research project / history item",
)
async def add_project(
    data: ResearchProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    proj = await ResearchProfileService.add_project(db, current_user.id, data)
    return ResearchProjectResponse.model_validate(proj)


@router.put(
    "/me/projects/{proj_id}",
    response_model=ResearchProjectResponse,
    summary="Update a research project",
)
async def update_project(
    proj_id: uuid.UUID,
    data: ResearchProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    proj = await ResearchProfileService.update_project(
        db, current_user.id, proj_id, data
    )
    return ResearchProjectResponse.model_validate(proj)


@router.delete(
    "/me/projects/{proj_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a research project",
)
async def delete_project(
    proj_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await ResearchProfileService.delete_project(db, current_user.id, proj_id)


# ── Search & Public Detail endpoints ─────────────────────────────────────────
@router.get(
    "/search",
    response_model=ResearcherSearchResult,
    summary="Search and filter researcher profiles",
)
async def search_researchers(
    q: Optional[str] = Query(None, description="Free text search (name, org, bio, domains)"),
    domain: Optional[str] = Query(None, description="Filter by research domain"),
    tech_interest: Optional[str] = Query(None, description="Filter by technology interest"),
    org_type: Optional[str] = Query(None, description="Filter by organization type"),
    min_h_index: Optional[int] = Query(None, ge=0, description="Minimum h-index"),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    profiles, total = await ResearchProfileService.search_researchers(
        db,
        q=q,
        domain=domain,
        tech_interest=tech_interest,
        org_type=org_type,
        min_h_index=min_h_index,
        page=page,
        page_size=page_size,
    )

    items = [_map_profile_response(p) for p in profiles]
    return ResearcherSearchResult(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{id}",
    response_model=ResearchProfileResponse,
    summary="Get public research profile by profile ID or user ID",
)
async def get_public_research_profile(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    profile = await ResearchProfileService.get_profile_by_id(db, id)
    return _map_profile_response(profile)
