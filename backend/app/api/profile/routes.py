from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import requests

from app.core.limiter import limiter

from app.db.database import get_db
from app.schemas.research_profile import ResearchProfileCreate, ResearchProfileResponse
from app.crud.research_profile import create_or_update_profile, get_profile_by_user_id
from app.core.security import get_current_user
from app.crud.user import get_user_by_email

from app.schemas.publication import PublicationCreate, PublicationResponse
from app.schemas.patent import PatentCreate, PatentResponse
from app.crud.publication import (
    create_publication,
    get_publications_by_profile,
    get_publication_trend,
    get_emerging_topics,
    get_research_hotspots,
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
from app.crud.funding import get_recommended_funding
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
        create_publication(db, profile.id, pub_data)
        imported += 1

    return {"imported": imported, "total": len(publications)}


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