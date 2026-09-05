from sqlalchemy.orm import Session
from app.models.profile_entities import (
    ResearchDomain,
    ResearchKeyword,
    TechnologyArea,
    OrganizationInformation,
)
from app.models.research_profile import ResearchProfile


def _sync_csv_field(db: Session, profile: ResearchProfile, field_name: str, names: list[str]):
    """
    Keeps ResearchProfile.<field_name> (a comma-separated string) in sync
    with the normalized entity list, since many existing features
    (funding matching, explanation service, grant prediction, patent
    landscape, chatbot context, startup search) read that field directly.
    """
    setattr(profile, field_name, ", ".join(names))
    db.commit()


# ---------------- Research Domains ----------------

def add_research_domain(db: Session, profile: ResearchProfile, name: str):
    existing = (
        db.query(ResearchDomain)
        .filter(ResearchDomain.research_profile_id == profile.id, ResearchDomain.name == name)
        .first()
    )
    if existing:
        return existing, False

    domain = ResearchDomain(research_profile_id=profile.id, name=name)
    db.add(domain)
    db.commit()
    db.refresh(domain)

    all_names = [d.name for d in get_research_domains(db, profile.id)]
    _sync_csv_field(db, profile, "research_domains", all_names)
    return domain, True


def get_research_domains(db: Session, profile_id: int):
    return db.query(ResearchDomain).filter(ResearchDomain.research_profile_id == profile_id).all()


def delete_research_domain(db: Session, profile: ResearchProfile, domain_id: int):
    domain = (
        db.query(ResearchDomain)
        .filter(ResearchDomain.id == domain_id, ResearchDomain.research_profile_id == profile.id)
        .first()
    )
    if not domain:
        return False

    db.delete(domain)
    db.commit()

    all_names = [d.name for d in get_research_domains(db, profile.id)]
    _sync_csv_field(db, profile, "research_domains", all_names)
    return True


# ---------------- Research Keywords ----------------

def add_research_keyword(db: Session, profile: ResearchProfile, name: str):
    existing = (
        db.query(ResearchKeyword)
        .filter(ResearchKeyword.research_profile_id == profile.id, ResearchKeyword.name == name)
        .first()
    )
    if existing:
        return existing, False

    keyword = ResearchKeyword(research_profile_id=profile.id, name=name)
    db.add(keyword)
    db.commit()
    db.refresh(keyword)

    all_names = [k.name for k in get_research_keywords(db, profile.id)]
    _sync_csv_field(db, profile, "keywords", all_names)
    return keyword, True


def get_research_keywords(db: Session, profile_id: int):
    return db.query(ResearchKeyword).filter(ResearchKeyword.research_profile_id == profile_id).all()


def delete_research_keyword(db: Session, profile: ResearchProfile, keyword_id: int):
    keyword = (
        db.query(ResearchKeyword)
        .filter(ResearchKeyword.id == keyword_id, ResearchKeyword.research_profile_id == profile.id)
        .first()
    )
    if not keyword:
        return False

    db.delete(keyword)
    db.commit()

    all_names = [k.name for k in get_research_keywords(db, profile.id)]
    _sync_csv_field(db, profile, "keywords", all_names)
    return True


# ---------------- Technology Areas ----------------

def add_technology_area(db: Session, profile: ResearchProfile, name: str):
    existing = (
        db.query(TechnologyArea)
        .filter(TechnologyArea.research_profile_id == profile.id, TechnologyArea.name == name)
        .first()
    )
    if existing:
        return existing, False

    tech_area = TechnologyArea(research_profile_id=profile.id, name=name)
    db.add(tech_area)
    db.commit()
    db.refresh(tech_area)

    all_names = [t.name for t in get_technology_areas(db, profile.id)]
    _sync_csv_field(db, profile, "technology_areas", all_names)
    return tech_area, True


def get_technology_areas(db: Session, profile_id: int):
    return db.query(TechnologyArea).filter(TechnologyArea.research_profile_id == profile_id).all()


def delete_technology_area(db: Session, profile: ResearchProfile, tech_area_id: int):
    tech_area = (
        db.query(TechnologyArea)
        .filter(TechnologyArea.id == tech_area_id, TechnologyArea.research_profile_id == profile.id)
        .first()
    )
    if not tech_area:
        return False

    db.delete(tech_area)
    db.commit()

    all_names = [t.name for t in get_technology_areas(db, profile.id)]
    _sync_csv_field(db, profile, "technology_areas", all_names)
    return True


# ---------------- Organization Information ----------------

def get_organization_info(db: Session, profile_id: int):
    return (
        db.query(OrganizationInformation)
        .filter(OrganizationInformation.research_profile_id == profile_id)
        .first()
    )


def upsert_organization_info(db: Session, profile: ResearchProfile, data: dict):
    org_info = get_organization_info(db, profile.id)

    if org_info:
        for field, value in data.items():
            setattr(org_info, field, value)
    else:
        org_info = OrganizationInformation(research_profile_id=profile.id, **data)
        db.add(org_info)

    db.commit()
    db.refresh(org_info)
    return org_info