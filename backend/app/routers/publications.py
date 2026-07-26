from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.auth.dependencies import get_current_user
from app.schemas.publication import PublicationCreate, PublicationResponse
from app.models.publication import Publication
from app.models.profile import ResearcherProfile
from app.services import publication_service

router = APIRouter(prefix="/publications", tags=["Publications"])


@router.get("/")
def list_publications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List all publications with pagination. Accessible by all roles."""
    return publication_service.get_all_publications(db, skip, limit)


@router.get("/trends")
def publication_trends(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return publication_service.get_publication_trends(db)


@router.get("/domain-analysis")
def domain_analysis(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return publication_service.get_domain_analysis(db)


@router.get("/year-analysis")
def year_analysis(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return publication_service.get_year_analysis(db)


@router.get("/keywords")
def top_keywords(
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return publication_service.get_top_keywords(db, limit)


@router.post("/", response_model=PublicationResponse, status_code=201)
def create_publication(
    pub: PublicationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Researchers can create publications.
    Organization is auto-set from their profile.
    """
    if current_user["role"] not in ("researcher", "administrator", "innovation_manager"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    # Auto-set organization from researcher's profile
    if current_user["role"] == "researcher":
        profile = db.query(ResearcherProfile).filter(
            ResearcherProfile.user_id == current_user["id"]
        ).first()
        if not profile:
            raise HTTPException(status_code=400, detail="Create a profile before adding publications")
        pub_data = pub.model_dump()
        pub_data["organization"] = profile.organization
    else:
        pub_data = pub.model_dump()

    new_pub = Publication(**pub_data)
    db.add(new_pub)
    db.commit()
    db.refresh(new_pub)
    return new_pub


@router.put("/{pub_id}", response_model=PublicationResponse)
def update_publication(
    pub_id: int,
    pub: PublicationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Researchers can only update publications from their own organization.
    Admins can update any publication.
    """
    db_pub = db.query(Publication).filter(Publication.id == pub_id).first()
    if not db_pub:
        raise HTTPException(status_code=404, detail="Publication not found")

    if current_user["role"] == "researcher":
        profile = db.query(ResearcherProfile).filter(
            ResearcherProfile.user_id == current_user["id"]
        ).first()
        if not profile or db_pub.organization != profile.organization:
            raise HTTPException(status_code=403, detail="You can only update your organization's publications")

    for key, value in pub.model_dump().items():
        setattr(db_pub, key, value)
    db.commit()
    db.refresh(db_pub)
    return db_pub


@router.delete("/{pub_id}")
def delete_publication(
    pub_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Researchers can only delete publications from their own organization.
    Admins can delete any publication.
    """
    db_pub = db.query(Publication).filter(Publication.id == pub_id).first()
    if not db_pub:
        raise HTTPException(status_code=404, detail="Publication not found")

    if current_user["role"] == "researcher":
        profile = db.query(ResearcherProfile).filter(
            ResearcherProfile.user_id == current_user["id"]
        ).first()
        if not profile or db_pub.organization != profile.organization:
            raise HTTPException(status_code=403, detail="You can only delete your organization's publications")

    db.delete(db_pub)
    db.commit()
    return {"message": "Publication deleted successfully"}
