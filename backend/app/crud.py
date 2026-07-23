from sqlalchemy.orm import Session
from fastapi import HTTPException

from app import models, schemas
from app.auth import hash_password
from app.models import ResearchProfile, Publication




def create_user(db: Session, user: schemas.UserCreate):

    if get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="An account with this email already exists")

    db_user = models.User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
        role=user.role
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()




def create_profile(db: Session, profile, current_user):

    existing_profile = db.query(ResearchProfile).filter(
        ResearchProfile.user_id == current_user.id
    ).first()

    if existing_profile:
        raise HTTPException(
            status_code=400,
            detail="Profile already exists"
        )

    db_profile = ResearchProfile(
        organization=profile.organization,
        research_domain=profile.research_domain,
        technology_area=profile.technology_area,
        keywords=profile.keywords,
        publication_count=profile.publication_count,
        patents=profile.patents,
        user_id=current_user.id
    )

    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)

    return db_profile


def get_profile(db: Session, current_user):
    return db.query(ResearchProfile).filter(
        ResearchProfile.user_id == current_user.id
    ).first()


def update_profile(db: Session, profile, current_user):

    db_profile = db.query(ResearchProfile).filter(
        ResearchProfile.user_id == current_user.id
    ).first()

    if not db_profile:
        return None

    db_profile.organization = profile.organization
    db_profile.research_domain = profile.research_domain
    db_profile.technology_area = profile.technology_area
    db_profile.keywords = profile.keywords
    db_profile.publication_count = profile.publication_count
    db_profile.patents = profile.patents

    db.commit()
    db.refresh(db_profile)

    return db_profile


def delete_profile(db: Session, current_user):

    db_profile = db.query(ResearchProfile).filter(
        ResearchProfile.user_id == current_user.id
    ).first()

    if not db_profile:
        return False

    db.delete(db_profile)
    db.commit()

    return True


def create_publication(db, publication, current_user):

    profile = db.query(ResearchProfile).filter(
        ResearchProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Research profile not found"
        )

    db_publication = Publication(
        title=publication.title,
        authors=publication.authors,
        journal=publication.journal,
        publication_year=publication.publication_year,
        doi=publication.doi,
        research_profile_id=profile.id
    )

    db.add(db_publication)
    db.commit()
    db.refresh(db_publication)

    return db_publication

def get_publications(db, current_user):

    profile = db.query(ResearchProfile).filter(
        ResearchProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Research profile not found"
        )

    return db.query(Publication).filter(
        Publication.research_profile_id == profile.id
    ).all()
    
    

def get_publication(db, publication_id, current_user):

    profile = db.query(ResearchProfile).filter(
        ResearchProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Research profile not found"
        )

    publication = db.query(Publication).filter(
        Publication.id == publication_id,
        Publication.research_profile_id == profile.id
    ).first()

    if not publication:
        raise HTTPException(
            status_code=404,
            detail="Publication not found"
        )

    return publication

def update_publication(db, publication_id, publication, current_user):

    profile = db.query(ResearchProfile).filter(
        ResearchProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Research profile not found"
        )

    db_publication = db.query(Publication).filter(
        Publication.id == publication_id,
        Publication.research_profile_id == profile.id
    ).first()

    if not db_publication:
        raise HTTPException(
            status_code=404,
            detail="Publication not found"
        )

    db_publication.title = publication.title
    db_publication.authors = publication.authors
    db_publication.journal = publication.journal
    db_publication.publication_year = publication.publication_year
    db_publication.doi = publication.doi

    db.commit()
    db.refresh(db_publication)

    return db_publication    
    
def delete_publication(db, publication_id, current_user):

    profile = db.query(ResearchProfile).filter(
        ResearchProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Research profile not found")
    publication = db.query(Publication).filter(
        Publication.id == publication_id,
        Publication.research_profile_id == profile.id
    ).first()

    if not publication:
        raise HTTPException(
            status_code=404,
            detail="Publication not found"
        )

    db.delete(publication)
    db.commit()

    return {"message": "Publication deleted"}   

def create_patent(db, patent, current_user):

    profile = db.query(ResearchProfile).filter(
        ResearchProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Research profile not found"
        )

    db_patent = models.Patent(
        title=patent.title,
        assignee=patent.assignee,
        filing_date=patent.filing_date,
        patent_number=patent.patent_number,
        technology_domain=patent.technology_domain,
        research_profile_id=profile.id
    )

    db.add(db_patent)
    db.commit()
    db.refresh(db_patent)

    return db_patent

def get_patents(db, current_user):

    profile = db.query(ResearchProfile).filter(
        ResearchProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Research profile not found"
        )

    return db.query(models.Patent).filter(
        models.Patent.research_profile_id == profile.id
    ).all()
    
def get_patent(db, patent_id, current_user):

    profile = db.query(ResearchProfile).filter(
        ResearchProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Research profile not found"
        )

    patent = db.query(models.Patent).filter(
        models.Patent.id == patent_id,
        models.Patent.research_profile_id == profile.id
    ).first()

    if not patent:
        raise HTTPException(
            status_code=404,
            detail="Patent not found"
        )

    return patent    
def update_patent(db, patent_id, patent, current_user):

    profile = db.query(ResearchProfile).filter(
        ResearchProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Research profile not found"
        )

    db_patent = db.query(models.Patent).filter(
        models.Patent.id == patent_id,
        models.Patent.research_profile_id == profile.id
    ).first()

    if not db_patent:
        raise HTTPException(
            status_code=404,
            detail="Patent not found"
        )

    db_patent.title = patent.title
    db_patent.assignee = patent.assignee
    db_patent.filing_date = patent.filing_date
    db_patent.patent_number = patent.patent_number
    db_patent.technology_domain = patent.technology_domain

    db.commit()
    db.refresh(db_patent)

    return db_patent
def delete_patent(db, patent_id, current_user):

    profile = db.query(ResearchProfile).filter(
        ResearchProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Research profile not found")
    patent = db.query(models.Patent).filter(
        models.Patent.id == patent_id,
        models.Patent.research_profile_id == profile.id
    ).first()

    if not patent:
        raise HTTPException(
            status_code=404,
            detail="Patent not found"
        )

    db.delete(patent)
    db.commit()

    return {"message": "Patent deleted"}


    
# ==========================
# Funding Opportunity CRUD
# ==========================

def create_funding(db, funding):

    db_funding = models.FundingOpportunity(
        title=funding.title,
        funding_agency=funding.funding_agency,
        research_domain=funding.research_domain,
        technology_area=funding.technology_area,
        keywords=funding.keywords,
        amount=funding.amount,
        deadline=funding.deadline,
        eligibility=funding.eligibility,
        description=funding.description,
        link=funding.link
    )

    db.add(db_funding)
    db.commit()
    db.refresh(db_funding)

    return db_funding


def get_all_funding(db):

    return db.query(models.FundingOpportunity).all()


def get_funding(db, funding_id):

    funding = db.query(models.FundingOpportunity).filter(
        models.FundingOpportunity.id == funding_id
    ).first()

    if not funding:
        raise HTTPException(
            status_code=404,
            detail="Funding opportunity not found"
        )

    return funding


def update_funding(db, funding_id, funding):

    db_funding = db.query(models.FundingOpportunity).filter(
        models.FundingOpportunity.id == funding_id
    ).first()

    if not db_funding:
        raise HTTPException(
            status_code=404,
            detail="Funding opportunity not found"
        )

    db_funding.title = funding.title
    db_funding.funding_agency = funding.funding_agency
    db_funding.research_domain = funding.research_domain
    db_funding.technology_area = funding.technology_area
    db_funding.keywords = funding.keywords
    db_funding.amount = funding.amount
    db_funding.deadline = funding.deadline
    db_funding.eligibility = funding.eligibility
    db_funding.description = funding.description
    db_funding.link = funding.link

    db.commit()
    db.refresh(db_funding)

    return db_funding


def delete_funding(db, funding_id):

    funding = db.query(models.FundingOpportunity).filter(
        models.FundingOpportunity.id == funding_id
    ).first()

    if not funding:
        raise HTTPException(
            status_code=404,
            detail="Funding opportunity not found"
        )

    db.delete(funding)
    db.commit()

    return {"message": "Funding opportunity deleted"}    

def _terms(value):
    return {term.strip().lower() for term in (value or "").replace(";", ",").split(",") if term.strip()}


def get_funding_recommendations(db, current_user):

    profile = db.query(models.ResearchProfile).filter(
        models.ResearchProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Research profile not found"
        )

    profile_terms = (
        _terms(profile.keywords)
        | _terms(profile.research_domain)
        | _terms(profile.technology_area)
    )

    recommendations = []

    for funding in db.query(models.FundingOpportunity).all():

        score = 0
        reasons = []

        if funding.research_domain.lower() == profile.research_domain.lower():
            score += 45
            reasons.append("Research domain matches")

        if funding.technology_area.lower() == profile.technology_area.lower():
            score += 35
            reasons.append("Technology area matches")

        keyword_matches = len(profile_terms & _terms(funding.keywords))
        if keyword_matches:
            score += min(20, keyword_matches * 10)
            reasons.append(f"{keyword_matches} keyword match(es)")

        if profile.organization.lower() in funding.eligibility.lower():
            score += 10
            reasons.append("Organization eligible")

        funding.score = min(score, 100)
        funding.reason = reasons

        recommendations.append(funding)

    recommendations.sort(
        key=lambda x: x.score,
        reverse=True
    )

    return recommendations

def get_grant_matches(db, current_user):

    profile = db.query(models.ResearchProfile).filter(
        models.ResearchProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Research profile not found"
        )

    profile_terms = (
        _terms(profile.keywords)
        | _terms(profile.research_domain)
        | _terms(profile.technology_area)
    )

    matched = []

    for funding in db.query(models.FundingOpportunity).all():

        score = 0

        if funding.research_domain.lower() == profile.research_domain.lower():
            score += 45

        if funding.technology_area.lower() == profile.technology_area.lower():
            score += 35

        score += min(
            20,
            len(profile_terms & _terms(funding.keywords)) * 10
        )

        if profile.organization.lower() in funding.eligibility.lower():
            score += 10

        matched.append({
            "title": funding.title,
            "funding_agency": funding.funding_agency,
            "research_domain": funding.research_domain,
            "technology_area": funding.technology_area,
            "match_score": min(score,100)
        })

    matched.sort(
        key=lambda x: x["match_score"],
        reverse=True
    )

    return matched


def get_dashboard_summary(db, current_user):

    profile = get_profile(db, current_user)

    if not profile:
        return {
            "research_profiles": 0,
            "publications": 0,
            "patents": 0,
            "funding_opportunities": db.query(models.FundingOpportunity).count(),
        }

    return {
        "research_profiles": 1,
        "publications": db.query(models.Publication)
            .filter(models.Publication.research_profile_id == profile.id)
            .count(),

        "patents": db.query(models.Patent)
            .filter(models.Patent.research_profile_id == profile.id)
            .count(),

        "funding_opportunities": db.query(models.FundingOpportunity).count(),
    }

from sqlalchemy import func

def publication_trends(db):

    trends = (
        db.query(
            models.Publication.publication_year,
            func.count(models.Publication.id).label("count")
        )
        .group_by(models.Publication.publication_year)
        .order_by(models.Publication.publication_year)
        .all()
    )

    return [
        {
            "year": year,
            "count": count
        }
        for year, count in trends
    ]