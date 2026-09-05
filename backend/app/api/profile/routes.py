import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import requests

from app.core.limiter import limiter

from app.db.database import get_db
from app.schemas.research_profile import ResearchProfileCreate, ResearchProfileResponse
from app.crud.research_profile import create_or_update_profile, get_profile_by_user_id
from app.schemas.profile_entities import (
    NamedEntityCreate,
    ResearchDomainResponse,
    ResearchKeywordResponse,
    TechnologyAreaResponse,
    OrganizationInfoUpdate,
    OrganizationInfoResponse,
)
from app.crud.profile_entities import (
    add_research_domain,
    get_research_domains,
    delete_research_domain,
    add_research_keyword,
    get_research_keywords,
    delete_research_keyword,
    add_technology_area,
    get_technology_areas,
    delete_technology_area,
    get_organization_info,
    upsert_organization_info,
)
from app.core.security import get_current_user
from app.crud.user import get_user_by_email

from app.schemas.publication import PublicationCreate, PublicationResponse, ExternalPublicationImport
from app.schemas.patent import PatentCreate, PatentResponse
from app.crud.publication import (
    create_publication,
    get_publications_by_profile,
    get_publication_trend,
    get_emerging_topics,
    get_research_hotspots,
    get_research_library,
    get_publication_by_id_for_profile,
    set_publication_pdf_path,
    search_openalex,
)
from app.crud.patent import (
    create_patent,
    get_patents_by_profile,
    get_patent_trend,
    get_competitor_analysis,
    get_technology_clusters,
    search_patentsview,
)
from app.crud.technology import get_technology_intelligence
from app.crud.innovation import get_innovation_score
from app.crud.commercialization import get_commercialization_recommendations
from app.services.openalex_service import search_author, extract_publications
from app.services.orcid_service import search_orcid_by_name, get_orcid_works
from app.services.crossref_service import search_crossref
from app.services.explanation_service import explain_funding_match
from app.services.grant_prediction_service import predict_grant_success
from app.services.patent_landscape_service import patent_landscape
from app.services.lens_service import LensNotConfiguredError
from app.crud.funding import get_recommended_funding, get_funding_by_id
from app.services.report_service import generate_pdf_report, generate_excel_report

router = APIRouter()


@router.post("/", response_model=ResearchProfileResponse)
def create_profile(
    profile_data: ResearchProfileCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_email = current_user.get("sub")
    db_user = get_user_by_email(db, user_email)

    profile = create_or_update_profile(db, db_user.id, profile_data)
    return profile


@router.get("/", response_model=ResearchProfileResponse)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_email = current_user.get("sub")
    db_user = get_user_by_email(db, user_email)

    profile = get_profile_by_user_id(db, db_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return profile


def _get_own_profile_or_404(db: Session, current_user: dict):
    user_email = current_user.get("sub")
    db_user = get_user_by_email(db, user_email)
    profile = get_profile_by_user_id(db, db_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Create your research profile first")
    return profile


# ---------------- Research Domains (granular) ----------------

@router.post("/domains", response_model=ResearchDomainResponse)
def add_domain(
    data: NamedEntityCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    profile = _get_own_profile_or_404(db, current_user)
    name = data.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Domain name cannot be empty")

    domain, created = add_research_domain(db, profile, name)
    if not created:
        raise HTTPException(status_code=400, detail="This research domain already exists")
    return domain


@router.get("/domains", response_model=List[ResearchDomainResponse])
def list_domains(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    profile = _get_own_profile_or_404(db, current_user)
    return get_research_domains(db, profile.id)


@router.delete("/domains/{domain_id}")
def remove_domain(
    domain_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    profile = _get_own_profile_or_404(db, current_user)
    deleted = delete_research_domain(db, profile, domain_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Research domain not found")
    return {"message": "Research domain deleted successfully"}


# ---------------- Research Keywords (granular) ----------------

@router.post("/keywords", response_model=ResearchKeywordResponse)
def add_keyword(
    data: NamedEntityCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    profile = _get_own_profile_or_404(db, current_user)
    name = data.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Keyword cannot be empty")

    keyword, created = add_research_keyword(db, profile, name)
    if not created:
        raise HTTPException(status_code=400, detail="This keyword already exists")
    return keyword


@router.get("/keywords", response_model=List[ResearchKeywordResponse])
def list_keywords(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    profile = _get_own_profile_or_404(db, current_user)
    return get_research_keywords(db, profile.id)


@router.delete("/keywords/{keyword_id}")
def remove_keyword(
    keyword_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    profile = _get_own_profile_or_404(db, current_user)
    deleted = delete_research_keyword(db, profile, keyword_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Keyword not found")
    return {"message": "Keyword deleted successfully"}


# ---------------- Technology Areas (granular) ----------------

@router.post("/technology-areas", response_model=TechnologyAreaResponse)
def add_tech_area(
    data: NamedEntityCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    profile = _get_own_profile_or_404(db, current_user)
    name = data.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Technology area cannot be empty")

    tech_area, created = add_technology_area(db, profile, name)
    if not created:
        raise HTTPException(status_code=400, detail="This technology area already exists")
    return tech_area


@router.get("/technology-areas", response_model=List[TechnologyAreaResponse])
def list_tech_areas(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    profile = _get_own_profile_or_404(db, current_user)
    return get_technology_areas(db, profile.id)


@router.delete("/technology-areas/{tech_area_id}")
def remove_tech_area(
    tech_area_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    profile = _get_own_profile_or_404(db, current_user)
    deleted = delete_technology_area(db, profile, tech_area_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Technology area not found")
    return {"message": "Technology area deleted successfully"}


# ---------------- Organization Information (extended) ----------------

@router.get("/organization-info", response_model=OrganizationInfoResponse)
def get_org_info(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    profile = _get_own_profile_or_404(db, current_user)
    org_info = get_organization_info(db, profile.id)
    if not org_info:
        raise HTTPException(status_code=404, detail="Organization information not set yet")
    return org_info


@router.put("/organization-info", response_model=OrganizationInfoResponse)
def update_org_info(
    data: OrganizationInfoUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    profile = _get_own_profile_or_404(db, current_user)
    return upsert_organization_info(db, profile, data.model_dump())


@router.post("/publications", response_model=PublicationResponse)
def add_publication(
    pub_data: PublicationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_email = current_user.get("sub")
    db_user = get_user_by_email(db, user_email)
    profile = get_profile_by_user_id(db, db_user.id)

    if not profile:
        raise HTTPException(status_code=404, detail="Create your research profile first")

    return create_publication(db, profile.id, pub_data)


@router.get("/publications", response_model=List[PublicationResponse])
def list_publications(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_email = current_user.get("sub")
    db_user = get_user_by_email(db, user_email)
    profile = get_profile_by_user_id(db, db_user.id)

    if not profile:
        return []

    return get_publications_by_profile(db, profile.id)


@router.get("/publications/search-openalex")
@limiter.limit("10/minute")
def publications_search_openalex(
    request: Request,
    query: str,
    current_user: dict = Depends(get_current_user),
):
    return search_openalex(query)


# ---------------- Research Library (external, reference-only publications) ----------------
# Distinct from "My Publications": these are papers the researcher found via
# OpenAlex search and saved for reference, not papers they authored themselves.

@router.post("/library", response_model=PublicationResponse)
def add_to_research_library(
    pub_data: ExternalPublicationImport,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_email = current_user.get("sub")
    db_user = get_user_by_email(db, user_email)
    profile = get_profile_by_user_id(db, db_user.id)

    if not profile:
        raise HTTPException(status_code=404, detail="Create your research profile first")

    return create_publication(
        db,
        profile.id,
        PublicationCreate(**pub_data.model_dump()),
        source_type="external",
    )


@router.get("/library", response_model=List[PublicationResponse])
def list_research_library(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_email = current_user.get("sub")
    db_user = get_user_by_email(db, user_email)
    profile = get_profile_by_user_id(db, db_user.id)

    if not profile:
        return []

    return get_research_library(db, profile.id)


# ---------------- Publication PDF upload ----------------

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "uploads", "publications")


@router.post("/publications/{publication_id}/upload-pdf", response_model=PublicationResponse)
async def upload_publication_pdf(
    publication_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_email = current_user.get("sub")
    db_user = get_user_by_email(db, user_email)
    profile = get_profile_by_user_id(db, db_user.id)

    if not profile:
        raise HTTPException(status_code=404, detail="Create your research profile first")

    publication = get_publication_by_id_for_profile(db, publication_id, profile.id)
    if not publication:
        raise HTTPException(status_code=404, detail="Publication not found")

    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    safe_filename = f"{publication_id}_{uuid.uuid4().hex}.pdf"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    relative_path = f"uploads/publications/{safe_filename}"
    return set_publication_pdf_path(db, publication, relative_path)


@router.get("/publications/trend")
def publication_trend(db: Session = Depends(get_db)):
    return get_publication_trend(db)


@router.get("/publications/emerging-topics")
def emerging_topics(db: Session = Depends(get_db)):
    return get_emerging_topics(db)


@router.get("/publications/research-hotspots")
def research_hotspots(db: Session = Depends(get_db)):
    return get_research_hotspots(db)


@router.post("/patents", response_model=PatentResponse)
def add_patent(
    patent_data: PatentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_email = current_user.get("sub")
    db_user = get_user_by_email(db, user_email)
    profile = get_profile_by_user_id(db, db_user.id)

    if not profile:
        raise HTTPException(status_code=404, detail="Create your research profile first")

    return create_patent(db, profile.id, patent_data)


@router.get("/patents", response_model=List[PatentResponse])
def list_patents(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_email = current_user.get("sub")
    db_user = get_user_by_email(db, user_email)
    profile = get_profile_by_user_id(db, db_user.id)

    if not profile:
        return []

    return get_patents_by_profile(db, profile.id)


@router.get("/patents/search-live")
@limiter.limit("10/minute")
def search_live_patents(
    request: Request,
    keyword: str,
    current_user: dict = Depends(get_current_user),
):
    return search_patentsview(keyword)


@router.get("/patents/trend")
def patent_trend(db: Session = Depends(get_db)):
    return get_patent_trend(db)


@router.get("/patents/competitor-analysis")
def competitor_analysis(db: Session = Depends(get_db)):
    return get_competitor_analysis(db)


@router.get("/patents/technology-clusters")
def technology_clusters(db: Session = Depends(get_db)):
    return get_technology_clusters(db)


@router.get("/technology-intelligence")
def technology_intelligence(db: Session = Depends(get_db)):
    return get_technology_intelligence(db)


@router.get("/innovation-score")
def innovation_score(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_email = current_user.get("sub")
    db_user = get_user_by_email(db, user_email)
    profile = get_profile_by_user_id(db, db_user.id)

    if not profile:
        raise HTTPException(status_code=404, detail="Create your research profile first")

    return get_innovation_score(db, profile)


@router.get("/commercialization-recommendations")
def commercialization_recommendations(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_email = current_user.get("sub")
    db_user = get_user_by_email(db, user_email)
    profile = get_profile_by_user_id(db, db_user.id)

    if not profile:
        raise HTTPException(status_code=404, detail="Create your research profile first")

    return get_commercialization_recommendations(db, profile)


# ---------------- OpenAlex Integration ----------------

@router.get("/openalex/search-author")
@limiter.limit("10/minute")
def openalex_search_author(
    request: Request,
    name: str,
    current_user: dict = Depends(get_current_user),
):
    try:
        authors = search_author(name)
        return {"count": len(authors), "authors": authors}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Could not reach OpenAlex: {e}")


@router.get("/openalex/author-publications")
def openalex_author_publications(
    author_id: str,
    current_user: dict = Depends(get_current_user),
):
    try:
        publications = extract_publications(author_id)
        return {"count": len(publications), "publications": publications}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Could not reach OpenAlex: {e}")


@router.post("/openalex/import-publications")
def openalex_import_publications(
    author_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_email = current_user.get("sub")
    db_user = get_user_by_email(db, user_email)
    profile = get_profile_by_user_id(db, db_user.id)

    if not profile:
        raise HTTPException(status_code=404, detail="Create your research profile first")

    try:
        publications = extract_publications(author_id)
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Could not reach OpenAlex: {e}")

    imported = 0
    for item in publications:
        if not item.get("title"):
            continue
        pub_data = PublicationCreate(
            title=item["title"],
            authors=item.get("authors"),
            year=item.get("year"),
            source=item.get("source"),
            link=item.get("link"),
        )
        create_publication(db, profile.id, pub_data, source_type="external")
        imported += 1

    return {"imported": imported, "total": len(publications)}


# ---------------- ORCID Integration ----------------

@router.get("/orcid/search")
@limiter.limit("10/minute")
def orcid_search(
    request: Request,
    name: str,
    current_user: dict = Depends(get_current_user),
):
    return search_orcid_by_name(name)


@router.get("/orcid/works")
@limiter.limit("10/minute")
def orcid_works(
    request: Request,
    orcid_id: str,
    current_user: dict = Depends(get_current_user),
):
    try:
        return get_orcid_works(orcid_id)
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Could not reach ORCID: {e}")


@router.post("/orcid/import")
@limiter.limit("5/minute")
def orcid_import(
    request: Request,
    orcid_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Imports every work on a researcher's public ORCID profile into their
    Research Library (external, reference publications) and saves the
    ORCID iD on their profile for future reference.
    """
    user_email = current_user.get("sub")
    db_user = get_user_by_email(db, user_email)
    profile = get_profile_by_user_id(db, db_user.id)

    if not profile:
        raise HTTPException(status_code=404, detail="Create your research profile first")

    try:
        works = get_orcid_works(orcid_id)
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Could not reach ORCID: {e}")

    imported = 0
    for item in works:
        if not item.get("title"):
            continue
        pub_data = PublicationCreate(
            title=item["title"],
            authors=item.get("authors"),
            year=item.get("year"),
            source=item.get("source"),
            link=item.get("link"),
        )
        create_publication(db, profile.id, pub_data, source_type="external")
        imported += 1

    profile.orcid_id = orcid_id.strip()
    db.commit()

    return {"imported": imported, "total": len(works)}


# ---------------- Crossref Integration ----------------

@router.get("/crossref/search")
@limiter.limit("10/minute")
def crossref_search(
    request: Request,
    query: str,
    current_user: dict = Depends(get_current_user),
):
    return search_crossref(query)


# ---------------- Explanation Service ----------------

@router.get("/funding/{funding_id}/explanation")
def funding_explanation(
    funding_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_email = current_user.get("sub")
    db_user = get_user_by_email(db, user_email)
    profile = get_profile_by_user_id(db, db_user.id)

    if not profile:
        raise HTTPException(status_code=404, detail="Create your research profile first")

    funding = get_funding_by_id(db, funding_id)
    if not funding:
        raise HTTPException(status_code=404, detail="Funding opportunity not found")

    return explain_funding_match(profile.research_domains, funding, db_user.role)


@router.get("/funding/{funding_id}/predict-success")
def predict_funding_success(
    funding_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_email = current_user.get("sub")
    db_user = get_user_by_email(db, user_email)
    profile = get_profile_by_user_id(db, db_user.id)

    if not profile:
        raise HTTPException(status_code=404, detail="Create your research profile first")

    funding = get_funding_by_id(db, funding_id)
    if not funding:
        raise HTTPException(status_code=404, detail="Funding opportunity not found")

    return predict_grant_success(db, profile, funding)


# ---------------- Global Patent Landscape (Lens.org) ----------------

@router.get("/patent-landscape")
@limiter.limit("10/minute")
def global_patent_landscape(
    request: Request,
    query: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_email = current_user.get("sub")
    db_user = get_user_by_email(db, user_email)
    profile = get_profile_by_user_id(db, db_user.id) if db_user else None
    publications = get_publications_by_profile(db, profile.id) if profile else []

    try:
        return patent_landscape(query, profile, publications)
    except LensNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


# ---------------- Notifications (computed live from real data) ----------------

@router.get("/notifications")
def get_notifications(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_email = current_user.get("sub")
    db_user = get_user_by_email(db, user_email)
    profile = get_profile_by_user_id(db, db_user.id)

    notifications = []

    if not profile:
        notifications.append(
            {
                "id": "no-profile",
                "type": "profile",
                "message": "Create your research profile to unlock funding matches and your innovation score.",
            }
        )
        return {"count": len(notifications), "notifications": notifications}

    matched_funding = get_recommended_funding(db, profile.research_domains, db_user.role)
    if matched_funding:
        for f in matched_funding[:3]:
            notifications.append(
                {
                    "id": f"funding-{f.id}",
                    "type": "funding",
                    "message": f"New funding match: \"{f.title}\" ({f.amount})",
                }
            )

    publications = get_publications_by_profile(db, profile.id)
    for p in sorted(publications, key=lambda x: x.id, reverse=True)[:2]:
        notifications.append(
            {
                "id": f"publication-{p.id}",
                "type": "publication",
                "message": f"Publication on record: \"{p.title}\"",
            }
        )

    patents = get_patents_by_profile(db, profile.id)
    for pt in sorted(patents, key=lambda x: x.id, reverse=True)[:2]:
        notifications.append(
            {
                "id": f"patent-{pt.id}",
                "type": "patent",
                "message": f"Patent on record: \"{pt.title}\" ({pt.assignee})",
            }
        )

    score_data = get_innovation_score(db, profile)
    notifications.append(
        {
            "id": "innovation-score",
            "type": "innovation",
            "message": f"Your Innovation Score is {score_data['innovation_score']} — {score_data['rating']}",
        }
    )

    return {"count": len(notifications), "notifications": notifications}


# ---------------- Reports & Export (PDF / Excel) ----------------

def _gather_report_data(db: Session, current_user: dict):
    user_email = current_user.get("sub")
    db_user = get_user_by_email(db, user_email)
    profile = get_profile_by_user_id(db, db_user.id)

    if not profile:
        raise HTTPException(status_code=404, detail="Create your research profile first")

    score_data = get_innovation_score(db, profile)
    publications = get_publications_by_profile(db, profile.id)
    patents = get_patents_by_profile(db, profile.id)
    funding_matches = get_recommended_funding(db, profile.research_domains, db_user.role)
    commercialization = get_commercialization_recommendations(db, profile)

    return profile, score_data, publications, patents, funding_matches, commercialization


@router.get("/reports/pdf")
def download_pdf_report(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    profile, score_data, publications, patents, funding_matches, commercialization = _gather_report_data(
        db, current_user
    )

    buffer = generate_pdf_report(
        profile, score_data, publications, patents, funding_matches, commercialization
    )

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=innovation_report.pdf"},
    )


@router.get("/reports/excel")
def download_excel_report(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    profile, score_data, publications, patents, funding_matches, commercialization = _gather_report_data(
        db, current_user
    )

    buffer = generate_excel_report(profile, score_data, publications, patents, funding_matches)

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=innovation_report.xlsx"},
    )