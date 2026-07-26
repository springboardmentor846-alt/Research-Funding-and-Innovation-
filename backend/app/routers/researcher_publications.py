from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.researcher_publication import Publication
from app.schemas.researcher_publication import PublicationCreate, PublicationResponse
from app.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/my-publications",
    tags=["My Publications"]
)


# ----------------------------
# Create Publication
# ----------------------------
@router.post("/", response_model=PublicationResponse, status_code=201)
def create_publication(
    pub: PublicationCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "researcher":
        raise HTTPException(
            status_code=403,
            detail="Only researchers can manage publications"
        )

    new_pub = Publication(
        user_id=current_user["id"],
        title=pub.title,
        authors=pub.authors,
        publication_type=pub.publication_type,
        journal_or_conference=pub.journal_or_conference,
        publication_year=pub.publication_year,
        doi=pub.doi,
        abstract=pub.abstract,
        keywords=pub.keywords,
        pdf_url=pub.pdf_url
    )

    db.add(new_pub)
    db.commit()
    db.refresh(new_pub)

    return new_pub


# ----------------------------
# Get My Publications
# ----------------------------
@router.get("/", response_model=list[PublicationResponse])
def get_my_publications(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "researcher":
        raise HTTPException(
            status_code=403,
            detail="Only researchers can manage publications"
        )

    return db.query(Publication).filter(
        Publication.user_id == current_user["id"]
    ).all()


# ----------------------------
# Get Single Publication
# ----------------------------
@router.get("/{pub_id}", response_model=PublicationResponse)
def get_publication(
    pub_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "researcher":
        raise HTTPException(
            status_code=403,
            detail="Only researchers can manage publications"
        )

    pub = db.query(Publication).filter(
        Publication.id == pub_id,
        Publication.user_id == current_user["id"]
    ).first()

    if not pub:
        raise HTTPException(
            status_code=404,
            detail="Publication not found"
        )

    return pub


# ----------------------------
# Update Publication
# ----------------------------
@router.put("/{pub_id}", response_model=PublicationResponse)
def update_publication(
    pub_id: int,
    pub: PublicationCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "researcher":
        raise HTTPException(
            status_code=403,
            detail="Only researchers can manage publications"
        )

    db_pub = db.query(Publication).filter(
        Publication.id == pub_id,
        Publication.user_id == current_user["id"]
    ).first()

    if not db_pub:
        raise HTTPException(
            status_code=404,
            detail="Publication not found"
        )

    db_pub.title = pub.title
    db_pub.authors = pub.authors
    db_pub.publication_type = pub.publication_type
    db_pub.journal_or_conference = pub.journal_or_conference
    db_pub.publication_year = pub.publication_year
    db_pub.doi = pub.doi
    db_pub.abstract = pub.abstract
    db_pub.keywords = pub.keywords
    db_pub.pdf_url = pub.pdf_url

    db.commit()
    db.refresh(db_pub)

    return db_pub


# ----------------------------
# Delete Publication
# ----------------------------
@router.delete("/{pub_id}")
def delete_publication(
    pub_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "researcher":
        raise HTTPException(
            status_code=403,
            detail="Only researchers can manage publications"
        )

    pub = db.query(Publication).filter(
        Publication.id == pub_id,
        Publication.user_id == current_user["id"]
    ).first()

    if not pub:
        raise HTTPException(
            status_code=404,
            detail="Publication not found"
        )

    db.delete(pub)
    db.commit()

    return {"message": "Publication deleted successfully"}
