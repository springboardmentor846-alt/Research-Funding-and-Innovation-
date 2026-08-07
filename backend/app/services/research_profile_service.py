"""
Service layer for Research Profile, Publications, Patents, Projects, and Search/Filters.
"""
import os
import uuid
from typing import List, Optional, Tuple
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select, func, or_, cast, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.research_profile import (
    ResearchProfile,
    Publication,
    Patent,
    ResearchProject,
)
from app.schemas.research_profile import (
    ResearchProfileUpdate,
    PublicationCreate,
    PublicationUpdate,
    PatentCreate,
    PatentUpdate,
    ResearchProjectCreate,
    ResearchProjectUpdate,
)

UPLOAD_DIR = "uploads/avatars"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


class ResearchProfileService:

    @staticmethod
    async def get_or_create_profile(
        db: AsyncSession, user_id: uuid.UUID
    ) -> ResearchProfile:
        """Fetch profile for user, auto-creating a default if none exists."""
        stmt = (
            select(ResearchProfile)
            .where(ResearchProfile.user_id == user_id)
            .options(
                selectinload(ResearchProfile.user),
                selectinload(ResearchProfile.publications),
                selectinload(ResearchProfile.patents),
                selectinload(ResearchProfile.projects),
            )
        )
        result = await db.execute(stmt)
        profile = result.scalar_one_or_none()

        if not profile:
            # Create default profile
            user_stmt = select(User).where(User.id == user_id)
            user_res = await db.execute(user_stmt)
            user = user_res.scalar_one_or_none()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )

            profile = ResearchProfile(
                user_id=user_id,
                organization_name=user.organization or "",
                position=user.position or "",
                summary_bio=user.bio or "",
                avatar_url=user.avatar_url,
                research_domains=[],
                keywords=[],
                technology_interests=[],
            )
            db.add(profile)
            await db.commit()
            await db.refresh(profile)

            # Re-fetch with relationships loaded
            result = await db.execute(stmt)
            profile = result.scalar_one()

        return profile

    @staticmethod
    async def update_profile(
        db: AsyncSession, user_id: uuid.UUID, data: ResearchProfileUpdate
    ) -> ResearchProfile:
        profile = await ResearchProfileService.get_or_create_profile(db, user_id)

        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(profile, key, value)

        await db.commit()
        return await ResearchProfileService.get_or_create_profile(db, user_id)

    @staticmethod
    async def upload_avatar(
        db: AsyncSession, user_id: uuid.UUID, file: UploadFile
    ) -> str:
        """Validate and save user profile avatar image."""
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided"
            )

        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file extension. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
            )

        # Read content to verify size
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size exceeds maximum limit of 5MB",
            )

        os.makedirs(UPLOAD_DIR, exist_ok=True)
        filename = f"avatar_{user_id}_{uuid.uuid4().hex[:8]}{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)

        with open(filepath, "wb") as f:
            f.write(content)

        avatar_url = f"/uploads/avatars/{filename}"

        # Update profile avatar_url
        profile = await ResearchProfileService.get_or_create_profile(db, user_id)
        profile.avatar_url = avatar_url

        # Also update user table avatar_url for consistency
        user_stmt = select(User).where(User.id == user_id)
        user_res = await db.execute(user_stmt)
        user = user_res.scalar_one_or_none()
        if user:
            user.avatar_url = avatar_url

        await db.commit()
        return avatar_url

    # ── Publications CRUD ─────────────────────────────────────────────────────
    @staticmethod
    async def add_publication(
        db: AsyncSession, user_id: uuid.UUID, data: PublicationCreate
    ) -> Publication:
        profile = await ResearchProfileService.get_or_create_profile(db, user_id)
        pub = Publication(profile_id=profile.id, **data.model_dump())
        db.add(pub)
        await db.commit()
        await db.refresh(pub)
        return pub

    @staticmethod
    async def update_publication(
        db: AsyncSession, user_id: uuid.UUID, pub_id: uuid.UUID, data: PublicationUpdate
    ) -> Publication:
        profile = await ResearchProfileService.get_or_create_profile(db, user_id)
        stmt = select(Publication).where(
            Publication.id == pub_id, Publication.profile_id == profile.id
        )
        res = await db.execute(stmt)
        pub = res.scalar_one_or_none()
        if not pub:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Publication not found"
            )

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(pub, key, value)

        await db.commit()
        await db.refresh(pub)
        return pub

    @staticmethod
    async def delete_publication(
        db: AsyncSession, user_id: uuid.UUID, pub_id: uuid.UUID
    ) -> None:
        profile = await ResearchProfileService.get_or_create_profile(db, user_id)
        stmt = select(Publication).where(
            Publication.id == pub_id, Publication.profile_id == profile.id
        )
        res = await db.execute(stmt)
        pub = res.scalar_one_or_none()
        if not pub:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Publication not found"
            )

        await db.delete(pub)
        await db.commit()

    # ── Patents CRUD ──────────────────────────────────────────────────────────
    @staticmethod
    async def add_patent(
        db: AsyncSession, user_id: uuid.UUID, data: PatentCreate
    ) -> Patent:
        profile = await ResearchProfileService.get_or_create_profile(db, user_id)
        pat = Patent(profile_id=profile.id, **data.model_dump())
        db.add(pat)
        await db.commit()
        await db.refresh(pat)
        return pat

    @staticmethod
    async def update_patent(
        db: AsyncSession, user_id: uuid.UUID, pat_id: uuid.UUID, data: PatentUpdate
    ) -> Patent:
        profile = await ResearchProfileService.get_or_create_profile(db, user_id)
        stmt = select(Patent).where(
            Patent.id == pat_id, Patent.profile_id == profile.id
        )
        res = await db.execute(stmt)
        pat = res.scalar_one_or_none()
        if not pat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Patent not found"
            )

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(pat, key, value)

        await db.commit()
        await db.refresh(pat)
        return pat

    @staticmethod
    async def delete_patent(
        db: AsyncSession, user_id: uuid.UUID, pat_id: uuid.UUID
    ) -> None:
        profile = await ResearchProfileService.get_or_create_profile(db, user_id)
        stmt = select(Patent).where(
            Patent.id == pat_id, Patent.profile_id == profile.id
        )
        res = await db.execute(stmt)
        pat = res.scalar_one_or_none()
        if not pat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Patent not found"
            )

        await db.delete(pat)
        await db.commit()

    # ── Projects CRUD ─────────────────────────────────────────────────────────
    @staticmethod
    async def add_project(
        db: AsyncSession, user_id: uuid.UUID, data: ResearchProjectCreate
    ) -> ResearchProject:
        profile = await ResearchProfileService.get_or_create_profile(db, user_id)
        proj = ResearchProject(profile_id=profile.id, **data.model_dump())
        db.add(proj)
        await db.commit()
        await db.refresh(proj)
        return proj

    @staticmethod
    async def update_project(
        db: AsyncSession,
        user_id: uuid.UUID,
        proj_id: uuid.UUID,
        data: ResearchProjectUpdate,
    ) -> ResearchProject:
        profile = await ResearchProfileService.get_or_create_profile(db, user_id)
        stmt = select(ResearchProject).where(
            ResearchProject.id == proj_id, ResearchProject.profile_id == profile.id
        )
        res = await db.execute(stmt)
        proj = res.scalar_one_or_none()
        if not proj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
            )

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(proj, key, value)

        await db.commit()
        await db.refresh(proj)
        return proj

    @staticmethod
    async def delete_project(
        db: AsyncSession, user_id: uuid.UUID, proj_id: uuid.UUID
    ) -> None:
        profile = await ResearchProfileService.get_or_create_profile(db, user_id)
        stmt = select(ResearchProject).where(
            ResearchProject.id == proj_id, ResearchProject.profile_id == profile.id
        )
        res = await db.execute(stmt)
        proj = res.scalar_one_or_none()
        if not proj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
            )

        await db.delete(proj)
        await db.commit()

    # ── Search & Filter ───────────────────────────────────────────────────────
    @staticmethod
    async def search_researchers(
        db: AsyncSession,
        q: Optional[str] = None,
        domain: Optional[str] = None,
        tech_interest: Optional[str] = None,
        org_type: Optional[str] = None,
        min_h_index: Optional[int] = None,
        page: int = 1,
        page_size: int = 12,
    ) -> Tuple[List[ResearchProfile], int]:
        stmt = (
            select(ResearchProfile)
            .join(User, ResearchProfile.user_id == User.id)
            .options(
                selectinload(ResearchProfile.user),
                selectinload(ResearchProfile.publications),
                selectinload(ResearchProfile.patents),
                selectinload(ResearchProfile.projects),
            )
        )

        conditions = []

        if q:
            term = f"%{q.lower()}%"
            conditions.append(
                or_(
                    func.lower(User.full_name).like(term),
                    func.lower(ResearchProfile.organization_name).like(term),
                    func.lower(ResearchProfile.department).like(term),
                    func.lower(ResearchProfile.field_of_study).like(term),
                    func.lower(ResearchProfile.summary_bio).like(term),
                    cast(ResearchProfile.research_domains, String).ilike(term),
                    cast(ResearchProfile.keywords, String).ilike(term),
                )
            )

        if domain:
            conditions.append(
                cast(ResearchProfile.research_domains, String).ilike(f"%{domain}%")
            )

        if tech_interest:
            conditions.append(
                cast(ResearchProfile.technology_interests, String).ilike(
                    f"%{tech_interest}%"
                )
            )

        if org_type:
            conditions.append(ResearchProfile.organization_type == org_type)

        if min_h_index is not None and min_h_index > 0:
            conditions.append(ResearchProfile.h_index >= min_h_index)

        if conditions:
            stmt = stmt.where(*conditions)

        # Count total matches
        count_stmt = select(func.count(ResearchProfile.id)).join(
            User, ResearchProfile.user_id == User.id
        )
        if conditions:
            count_stmt = count_stmt.where(*conditions)
        total_res = await db.execute(count_stmt)
        total = total_res.scalar() or 0

        # Pagination
        offset = (page - 1) * page_size
        stmt = stmt.order_by(ResearchProfile.updated_at.desc()).offset(offset).limit(page_size)

        result = await db.execute(stmt)
        profiles = list(result.scalars().all())

        return profiles, total

    @staticmethod
    async def get_profile_by_id(
        db: AsyncSession, profile_or_user_id: uuid.UUID
    ) -> ResearchProfile:
        stmt = (
            select(ResearchProfile)
            .where(
                or_(
                    ResearchProfile.id == profile_or_user_id,
                    ResearchProfile.user_id == profile_or_user_id,
                )
            )
            .options(
                selectinload(ResearchProfile.user),
                selectinload(ResearchProfile.publications),
                selectinload(ResearchProfile.patents),
                selectinload(ResearchProfile.projects),
            )
        )
        res = await db.execute(stmt)
        profile = res.scalar_one_or_none()
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Research profile not found",
            )
        return profile
