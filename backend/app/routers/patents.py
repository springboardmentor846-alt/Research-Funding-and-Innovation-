from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import require_role
from app import schemas, crud

router = APIRouter(
    prefix="/patents",
    tags=["Patents"]
)

@router.post("/", response_model=schemas.PatentResponse)
def create(
    patent: schemas.PatentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["Researcher"]))
):
    return crud.create_patent(db, patent, current_user)


@router.get("/", response_model=list[schemas.PatentResponse])
def get_all(
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["Researcher"]))
):
    return crud.get_patents(db, current_user)


@router.get("/{patent_id}", response_model=schemas.PatentResponse)
def get_one(
    patent_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["Researcher"]))
):
    return crud.get_patent(db, patent_id, current_user)


@router.put("/{patent_id}", response_model=schemas.PatentResponse)
def update(
    patent_id: int,
    patent: schemas.PatentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["Researcher"]))
):
    return crud.update_patent(db, patent_id, patent, current_user)


@router.delete("/{patent_id}")
def delete(
    patent_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["Researcher"]))
):
    return crud.delete_patent(db, patent_id, current_user)