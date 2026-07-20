from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_role
from app.models.user import User

from app.services.crossref_service import (
    get_publication_metadata
)

router = APIRouter(
    prefix="/crossref",
    tags=["Crossref"]
)


@router.get("/{doi:path}")
def get_metadata(
    doi: str,
    current_user: User = Depends(
        require_role("researcher")
    ),
    db: Session = Depends(get_db)
):

    try:
        metadata = get_publication_metadata(doi)

        return {
            "title": metadata.get("title", [None])[0],
            "publisher": metadata.get("publisher"),
            "journal": metadata.get(
                "container-title",
                [None]
            )[0],
            "type": metadata.get("type"),
            "doi": metadata.get("DOI"),
            "url": metadata.get("URL")
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )