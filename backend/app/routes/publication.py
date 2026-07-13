from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import verify_token

from app.models.user import User
from app.models.publication import Publication

from app.schemas.publication import PublicationCreate

router = APIRouter(
    tags=["Publication"]
)
@router.post("/publication")
def add_publication(
    publication: PublicationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):

    user = db.query(User).filter(
        User.email == current_user["sub"]
    ).first()

    new_publication = Publication(
        user_id=user.id,
        title=publication.title,
        authors=publication.authors,
        journal=publication.journal,
        year=publication.year,
        doi=publication.doi,
        citation_count=publication.citation_count,
        research_domain=publication.research_domain
    )

    db.add(new_publication)
    db.commit()
    db.refresh(new_publication)

    return {
        "message": "Publication Added Successfully",
        "publication_id": new_publication.id
    }


@router.get("/publications")
def view_publications(
    db: Session = Depends(get_db)
):
    return db.query(Publication).all()


@router.put("/publication/{publication_id}")
def update_publication(
    publication_id: int,
    publication: PublicationCreate,
    db: Session = Depends(get_db)
):

    db_publication = db.query(Publication).filter(
        Publication.id == publication_id
    ).first()

    if db_publication is None:
        raise HTTPException(
            status_code=404,
            detail="Publication Not Found"
        )

    db_publication.title = publication.title
    db_publication.authors = publication.authors
    db_publication.journal = publication.journal
    db_publication.year = publication.year
    db_publication.doi = publication.doi
    db_publication.citation_count = publication.citation_count
    db_publication.research_domain = publication.research_domain

    db.commit()
    db.refresh(db_publication)

    return {
        "message": "Publication Updated Successfully"
    }


@router.delete("/publication/{publication_id}")
def delete_publication(
    publication_id: int,
    db: Session = Depends(get_db)
):

    publication = db.query(Publication).filter(
        Publication.id == publication_id
    ).first()

    if publication is None:
        raise HTTPException(
            status_code=404,
            detail="Publication Not Found"
        )

    db.delete(publication)
    db.commit()

    return {
        "message": "Publication Deleted Successfully"
    }