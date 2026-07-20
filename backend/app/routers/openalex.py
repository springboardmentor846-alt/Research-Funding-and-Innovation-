from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_role

from app.models.user import User
from app.models.publication import Publication
from app.models.research_profile import ResearchProfile

from app.services.openalex_service import (
    search_author,
    get_author_works,
    extract_publications,
)

router = APIRouter(
    prefix="/openalex",
    tags=["OpenAlex"]
)


@router.get("/search-author")
def search_openalex_author(
    name: str = Query(..., min_length=2),
    current_user: User = Depends(
        require_role("researcher")
    ),
    db: Session = Depends(get_db)
):

    try:

        data = search_author(name)

        authors = []

        for author in data.get("results", []):

            authors.append(
                {
                    "id": author.get("id"),
                    "name": author.get("display_name"),
                    "works_count": author.get("works_count"),
                    "cited_by_count": author.get("cited_by_count"),
                    "orcid": author.get("orcid"),
                    "country": (
                        author.get("last_known_institutions", [{}])[0]
                        .get("country_code")
                        if author.get("last_known_institutions")
                        else None
                    )
                }
            )

        return {
            "count": len(authors),
            "authors": authors
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/author-publications")
def author_publications(
    author_id: str,
    current_user: User = Depends(
        require_role("researcher")
    ),
    db: Session = Depends(get_db)
):

    try:

        data = get_author_works(author_id)

        publications = []

        for work in data.get("results", []):

            publications.append(
                {
                    "title": work.get("display_name"),
                    "publication_year": work.get("publication_year"),
                    "doi": work.get("doi"),
                    "type": work.get("type"),
                    "cited_by_count": work.get("cited_by_count"),
                    "openalex_id": work.get("id")
                }
            )

        return {
            "count": len(publications),
            "publications": publications
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)


        )


@router.post("/import-publications")
def import_publications(
    author_id: str,
    current_user: User = Depends(
        require_role("researcher")
    ),
    db: Session = Depends(get_db)
):

    profile = db.scalar(
        select(ResearchProfile).where(
            ResearchProfile.user_id == current_user.id
        )
    )

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Research profile not found."
        )

    publications = extract_publications(author_id)

    imported = 0
    skipped = 0

    for item in publications:

        existing = None

        # Check duplicate by DOI
        if item.get("doi"):

            existing = db.scalar(
                select(Publication).where(
                    Publication.doi == item["doi"]
                )
            )

        # Otherwise check by OpenAlex ID
        elif item.get("openalex_id"):

            existing = db.scalar(
                select(Publication).where(
                    Publication.openalex_id == item["openalex_id"]
                )
            )

        if existing:

            skipped += 1
            continue

        publication = Publication(
            research_profile_id=profile.id,
            **item
        )

        db.add(publication)

        imported += 1

    db.commit()

    return {
        "imported": imported,
        "skipped": skipped,
        "total": len(publications)
    }