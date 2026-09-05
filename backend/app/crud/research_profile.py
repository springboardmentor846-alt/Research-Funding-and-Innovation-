from sqlalchemy.orm import Session
from app.models.research_profile import ResearchProfile
from app.schemas.research_profile import ResearchProfileCreate


def get_profile_by_user_id(db: Session, user_id: int):
    return db.query(ResearchProfile).filter(ResearchProfile.user_id == user_id).first()


def create_or_update_profile(db: Session, user_id: int, profile_data: ResearchProfileCreate):
    existing_profile = get_profile_by_user_id(db, user_id)

    if existing_profile:
        existing_profile.research_domains = profile_data.research_domains
        existing_profile.keywords = profile_data.keywords
        existing_profile.publications = profile_data.publications
        existing_profile.patents = profile_data.patents
        existing_profile.technology_areas = profile_data.technology_areas
        existing_profile.organization_name = profile_data.organization_name
        existing_profile.orcid_id = profile_data.orcid_id

        db.commit()
        db.refresh(existing_profile)
        return existing_profile

    new_profile = ResearchProfile(
        user_id=user_id,
        research_domains=profile_data.research_domains,
        keywords=profile_data.keywords,
        publications=profile_data.publications,
        patents=profile_data.patents,
        technology_areas=profile_data.technology_areas,
        organization_name=profile_data.organization_name,
        orcid_id=profile_data.orcid_id,
    )

    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return new_profile