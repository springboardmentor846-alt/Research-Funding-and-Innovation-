from sqlalchemy.orm import Session

from app.models.user_profile import UserProfile
from app.schemas.user_profile_schema import (
    UserProfileCreate,
    UserProfileUpdate
)


def create_profile(
    db: Session,
    profile: UserProfileCreate,
    current_user
):
    existing = db.query(UserProfile).filter(
        UserProfile.user_id == current_user["id"]
    ).first()

    if existing:
        raise ValueError("Profile already exists")

    new_profile = UserProfile(
        user_id=current_user["id"],
        full_name=profile.full_name,
        organization=profile.organization,
        designation=profile.designation,
        domain=profile.domain,
        skills=profile.skills,
        interests=profile.interests,
        bio=profile.bio,
        linkedin_url=str(profile.linkedin_url) if profile.linkedin_url else None,
        github_url=str(profile.github_url) if profile.github_url else None,
        website=str(profile.website) if profile.website else None,
        profile_image=profile.profile_image
    )

    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)

    return new_profile


def get_my_profile(
    db: Session,
    current_user
):
    return db.query(UserProfile).filter(
        UserProfile.user_id == current_user["id"]
    ).first()


def update_profile(
    db: Session,
    profile: UserProfileUpdate,
    current_user
):
    existing = db.query(UserProfile).filter(
        UserProfile.user_id == current_user["id"]
    ).first()

    if not existing:
        return None

    if profile.full_name is not None:
        existing.full_name = profile.full_name

    if profile.organization is not None:
        existing.organization = profile.organization

    if profile.designation is not None:
        existing.designation = profile.designation

    if profile.domain is not None:
        existing.domain = profile.domain

    if profile.skills is not None:
        existing.skills = profile.skills

    if profile.interests is not None:
        existing.interests = profile.interests

    if profile.bio is not None:
        existing.bio = profile.bio

    if profile.linkedin_url is not None:
        existing.linkedin_url = str(profile.linkedin_url)

    if profile.github_url is not None:
        existing.github_url = str(profile.github_url)

    if profile.website is not None:
        existing.website = str(profile.website)

    if profile.profile_image is not None:
        existing.profile_image = profile.profile_image

    db.commit()
    db.refresh(existing)

    return existing


def delete_profile(
    db: Session,
    current_user
):
    existing = db.query(UserProfile).filter(
        UserProfile.user_id == current_user["id"]
    ).first()

    if not existing:
        return None

    db.delete(existing)
    db.commit()

    return {
        "message": "Profile deleted successfully"
    }