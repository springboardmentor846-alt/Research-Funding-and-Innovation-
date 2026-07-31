import requests
import os
import shutil
import uuid
from fastapi.responses import FileResponse

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Query,
    status,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies import (
    get_db,
    require_role,
)

from app.models.publication import Publication
from app.models.research_profile import ResearchProfile
from app.models.researcher_imported_publication import (
    ResearcherImportedPublication,
)
from app.models.research_domain import ResearchDomain
from app.models.research_keyword import ResearchKeyword
from app.models.technology_area import TechnologyArea
from app.models.user import User

from app.schemas.publication import (
    PublicationCreate,
    PublicationUpdate,
)

from app.services.openalex_service import (
    get_publications_by_topic,
)

from app.services.ai_service import (
    build_researcher_text,
    build_publication_text,
    rank_recommendations,
)


router = APIRouter(
    prefix="/publications",
    tags=["Publications"]
)

UPLOAD_DIRECTORY = "uploads/publications"

os.makedirs(
    UPLOAD_DIRECTORY,
    exist_ok=True
)


# ============================================================
# HELPER
# ============================================================

def get_research_profile(
    current_user: User,
    db: Session
):

    profile = db.scalar(
        select(ResearchProfile).where(
            ResearchProfile.user_id
            == current_user.id
        )
    )

    if profile is None:

        raise HTTPException(
            status_code=404,
            detail="Research profile not found."
        )

    return profile


# ============================================================
# MY PUBLICATIONS
# ============================================================

@router.get("")
def get_my_publications(
    current_user: User = Depends(
        require_role("researcher")
    ),
    db: Session = Depends(get_db)
):

    profile = get_research_profile(
        current_user,
        db
    )

    publications = db.scalars(
        select(Publication).where(
            Publication.research_profile_id
            == profile.id
        )
    ).all()

    return {
        "count": len(publications),
        "publications": publications
    }


# ============================================================
# CREATE MY PUBLICATION
# ============================================================

@router.post(
    "",
    status_code=status.HTTP_201_CREATED
)
def create_publication(
    publication_data: PublicationCreate,
    current_user: User = Depends(
        require_role("researcher")
    ),
    db: Session = Depends(get_db)
):

    profile = get_research_profile(
        current_user,
        db
    )

    publication = Publication(

        research_profile_id=profile.id,

        **publication_data.model_dump()
    )

    db.add(publication)

    try:

        db.commit()

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=(
                "Unable to create publication. "
                "The DOI may already exist."
            )
        )

    db.refresh(publication)

    return {
        "message": (
            "Publication added successfully."
        ),
        "publication_id": publication.id
    }


# ============================================================
# IMPORT OPENALEX PUBLICATIONS
# ============================================================

@router.post("/import/openalex")
def import_openalex_publications(
    query: str = Query(
        ...,
        min_length=2,
        max_length=200
    ),
    limit: int = Query(
        10,
        ge=1,
        le=50
    ),
    current_user: User = Depends(
        require_role("researcher")
    ),
    db: Session = Depends(get_db)
):

    profile = get_research_profile(
        current_user,
        db
    )

    try:

        external_publications = (
            get_publications_by_topic(
                query=query,
                limit=limit
            )
        )

    except requests.RequestException as error:

        raise HTTPException(
            status_code=502,
            detail=(
                "Unable to retrieve "
                "publications from OpenAlex."
            )
        ) from error

    imported = 0

    already_saved = 0

    created_external = 0

    for publication_data in (
        external_publications
    ):

        openalex_id = publication_data.get(
            "openalex_id"
        )

        doi = publication_data.get(
            "doi"
        )

        publication = None

        # ----------------------------------------------------
        # Find existing global publication
        # ----------------------------------------------------

        if openalex_id:

            publication = db.scalar(
                select(Publication).where(
                    Publication.openalex_id
                    == openalex_id
                )
            )

        if publication is None and doi:

            publication = db.scalar(
                select(Publication).where(
                    Publication.doi == doi
                )
            )

        # ----------------------------------------------------
        # Create external publication
        # ----------------------------------------------------

        if publication is None:

            publication = Publication(
                **publication_data
            )

            # Very important:
            publication.research_profile_id = None

            db.add(publication)

            db.flush()

            created_external += 1

        # ----------------------------------------------------
        # Check researcher's library
        # ----------------------------------------------------

        existing_link = db.scalar(
            select(
                ResearcherImportedPublication
            ).where(

                ResearcherImportedPublication
                .research_profile_id
                == profile.id,

                ResearcherImportedPublication
                .publication_id
                == publication.id
            )
        )

        if existing_link:

            already_saved += 1

            continue

        # ----------------------------------------------------
        # Add to research library
        # ----------------------------------------------------

        library_entry = (
            ResearcherImportedPublication(

                research_profile_id=profile.id,

                publication_id=publication.id
            )
        )

        db.add(library_entry)

        imported += 1

    db.commit()

    return {

        "message": (
            "OpenAlex import completed."
        ),

        "query": query,

        "requested": limit,

        "found": len(
            external_publications
        ),

        "imported": imported,

        "already_saved": already_saved,

        "new_external_records": (
            created_external
        )
    }


# ============================================================
# RESEARCH LIBRARY
# ============================================================

@router.get("/library/imported")
def get_research_library(
    current_user: User = Depends(
        require_role("researcher")
    ),
    db: Session = Depends(get_db)
):

    profile = get_research_profile(
        current_user,
        db
    )

    publications = db.scalars(

        select(Publication)

        .join(
            ResearcherImportedPublication,

            ResearcherImportedPublication
            .publication_id
            == Publication.id
        )

        .where(

            ResearcherImportedPublication
            .research_profile_id
            == profile.id
        )

        .order_by(
            ResearcherImportedPublication
            .imported_at.desc()
        )

    ).all()

    return {

        "count": len(publications),

        "publications": publications
    }


# ============================================================
# REMOVE FROM RESEARCH LIBRARY
# ============================================================

@router.delete(
    "/library/{publication_id}"
)
def remove_from_research_library(
    publication_id: int,
    current_user: User = Depends(
        require_role("researcher")
    ),
    db: Session = Depends(get_db)
):

    profile = get_research_profile(
        current_user,
        db
    )

    library_entry = db.scalar(

        select(
            ResearcherImportedPublication
        ).where(

            ResearcherImportedPublication
            .research_profile_id
            == profile.id,

            ResearcherImportedPublication
            .publication_id
            == publication_id
        )
    )

    if library_entry is None:

        raise HTTPException(
            status_code=404,
            detail=(
                "Publication is not "
                "in your research library."
            )
        )

    db.delete(library_entry)

    db.commit()

    return {
        "message": (
            "Publication removed "
            "from research library."
        )
    }


# ============================================================
# AI RECOMMENDATIONS
# ============================================================

@router.get("/recommendations/ai")
def ai_publication_recommendations(
    current_user: User = Depends(
        require_role("researcher")
    ),
    db: Session = Depends(get_db)
):

    profile = get_research_profile(
        current_user,
        db
    )

    domains = db.scalars(
        select(ResearchDomain).where(
            ResearchDomain
            .research_profile_id
            == profile.id
        )
    ).all()

    keywords = db.scalars(
        select(ResearchKeyword).where(
            ResearchKeyword
            .research_profile_id
            == profile.id
        )
    ).all()

    technologies = db.scalars(
        select(TechnologyArea).where(
            TechnologyArea
            .research_profile_id
            == profile.id
        )
    ).all()

    researcher_text = (
        build_researcher_text(
            profile,
            domains,
            keywords,
            technologies
        )
    )

    # Only external literature.
    #
    # We should NOT recommend the researcher's
    # own publications back to them.

    publications = db.scalars(

        select(Publication).where(

            Publication
            .research_profile_id
            .is_(None)
        )

    ).all()

    recommendations = (
        rank_recommendations(

            researcher_text=researcher_text,

            items=publications,

            text_builder=(
                build_publication_text
            ),

            subtitle_field="publisher"
        )
    )

    return {

        "researcher": current_user.email,

        "total_matches": len(
            recommendations
        ),

        "recommendations": (
            recommendations
        )
    }


# ============================================================
# GET MY PUBLICATION
# ============================================================
@router.post("/{publication_id}/pdf")
def upload_publication_pdf(
    publication_id: int,
    file: UploadFile = File(...),
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

    publication = db.scalar(
        select(Publication).where(
            Publication.id == publication_id,
            Publication.research_profile_id == profile.id
        )
    )

    if publication is None:
        raise HTTPException(
            status_code=404,
            detail="Publication not found."
        )

    # Only PDFs
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    # Check size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    max_size = 10 * 1024 * 1024

    if file_size > max_size:
        raise HTTPException(
            status_code=400,
            detail="PDF must be 10 MB or smaller."
        )

    # Delete old PDF when replacing one
    if (
        publication.pdf_path
        and os.path.exists(publication.pdf_path)
    ):
        os.remove(publication.pdf_path)

    unique_filename = (
        f"{publication.id}_{uuid.uuid4().hex}.pdf"
    )

    file_path = os.path.join(
        UPLOAD_DIRECTORY,
        unique_filename
    )

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer
            )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Unable to save publication PDF."
        ) from error

    publication.pdf_path = file_path

    db.commit()
    db.refresh(publication)

    return {
        "message": "Publication PDF uploaded successfully.",
        "publication_id": publication.id,
        "pdf_uploaded": True
    }



# ============================================================
# VIEW MY PUBLICATION PDF
# ============================================================

@router.get("/{publication_id}/pdf")
def get_publication_pdf(
    publication_id: int,
    current_user: User = Depends(
        require_role("researcher")
    ),
    db: Session = Depends(get_db)
):
    profile = get_research_profile(
        current_user,
        db
    )

    publication = db.scalar(
        select(Publication).where(
            Publication.id == publication_id,
            Publication.research_profile_id == profile.id
        )
    )

    if publication is None:
        raise HTTPException(
            status_code=404,
            detail="Publication not found."
        )

    if not publication.pdf_path:
        raise HTTPException(
            status_code=404,
            detail="No PDF uploaded for this publication."
        )

    if not os.path.exists(publication.pdf_path):
        raise HTTPException(
            status_code=404,
            detail="Publication PDF file not found."
        )

    return FileResponse(
        path=publication.pdf_path,
        media_type="application/pdf",
        filename=os.path.basename(
            publication.pdf_path
        )
    )





@router.get("/{publication_id}")
def get_publication(
    publication_id: int,
    current_user: User = Depends(
        require_role("researcher")
    ),
    db: Session = Depends(get_db)
):

    profile = get_research_profile(
        current_user,
        db
    )

    publication = db.scalar(

        select(Publication).where(

            Publication.id
            == publication_id,

            Publication.research_profile_id
            == profile.id
        )
    )

    if publication is None:

        raise HTTPException(
            status_code=404,
            detail="Publication not found."
        )

    return publication


# ============================================================
# UPDATE MY PUBLICATION
# ============================================================

@router.patch("/{publication_id}")
def update_publication(
    publication_id: int,
    publication_data: PublicationUpdate,
    current_user: User = Depends(
        require_role("researcher")
    ),
    db: Session = Depends(get_db)
):

    profile = get_research_profile(
        current_user,
        db
    )

    publication = db.scalar(

        select(Publication).where(

            Publication.id
            == publication_id,

            Publication.research_profile_id
            == profile.id
        )
    )

    if publication is None:

        raise HTTPException(
            status_code=404,
            detail="Publication not found."
        )

    update_data = (
        publication_data.model_dump(
            exclude_unset=True
        )
    )

    for key, value in (
        update_data.items()
    ):

        setattr(
            publication,
            key,
            value
        )

    db.commit()

    db.refresh(publication)

    return {
        "message": (
            "Publication updated successfully."
        )
    }


# ============================================================
# DELETE MY PUBLICATION
# ============================================================

@router.delete("/{publication_id}")
def delete_publication(
    publication_id: int,
    current_user: User = Depends(
        require_role("researcher")
    ),
    db: Session = Depends(get_db)
):

    profile = get_research_profile(
        current_user,
        db
    )

    publication = db.scalar(

        select(Publication).where(

            Publication.id
            == publication_id,

            Publication.research_profile_id
            == profile.id
        )
    )

    if publication is None:

        raise HTTPException(
            status_code=404,
            detail="Publication not found."
        )

    db.delete(publication)

    db.commit()

    return {
        "message": (
            "Publication deleted successfully."
        )
    }