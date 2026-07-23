from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import require_role
from app import schemas, crud

router = APIRouter(
    prefix="/publications",
    tags=["Publications"]
)


@router.post("/", response_model=schemas.PublicationResponse)
def create(
    publication: schemas.PublicationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["Researcher"]))
):
    return crud.create_publication(
        db,
        publication,
        current_user
    )


@router.get("/", response_model=list[schemas.PublicationResponse])
def get_all(
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["Researcher"]))
):
    return crud.get_publications(
        db,
        current_user
    )


@router.delete("/{publication_id}")
def delete(
    publication_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["Researcher"]))
):
    return crud.delete_publication(
        db,
        publication_id,
        current_user
    )
    
@router.get("/{publication_id}", response_model=schemas.PublicationResponse)
def get_one(
    publication_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["Researcher"]))
):
    return crud.get_publication(
        db,
        publication_id,
        current_user
    )
    
@router.put("/{publication_id}", response_model=schemas.PublicationResponse)
def update(
    publication_id: int,
    publication: schemas.PublicationUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["Researcher"]))
):
    return crud.update_publication(
        db,
        publication_id,
        publication,
        current_user
    )        