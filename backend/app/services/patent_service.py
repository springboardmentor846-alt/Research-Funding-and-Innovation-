import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

LENS_API_TOKEN = os.getenv("LENS_API_TOKEN")

LENS_SEARCH_URL = "https://api.lens.org/patent/search"


def search_patents(query: str, size: int = 10):

    headers = {
        "Authorization": f"Bearer {LENS_API_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "query": {
            "match": {
                "title": query
            }
        },
        "size": size
    }

    response = requests.post(
        LENS_SEARCH_URL,
        json=payload,
        headers=headers
    )

    return response.json()


def format_patents(results):
    patents = []

    for item in results:

        biblio = item.get("biblio", {})

        # Patent Title
        title = ""
        if biblio.get("invention_title"):
            title = biblio["invention_title"][0].get("text", "")

        # Applicant
        applicant = ""
        applicants = biblio.get("parties", {}).get("applicants", [])
        if applicants:
            applicant = applicants[0].get(
                "extracted_name", {}
            ).get("value", "")

        # Inventor
        inventor = ""
        inventors = biblio.get("parties", {}).get("inventors", [])
        if inventors:
            inventor = inventors[0].get(
                "extracted_name", {}
            ).get("value", "")

        patents.append({
            "lens_id": item.get("lens_id"),
            "title": title,
            "applicant": applicant,
            "inventor": inventor,
            "publication_date": item.get("date_published"),
            "jurisdiction": item.get("jurisdiction"),
            "legal_status": item.get("legal_status", {}).get(
                "patent_status", ""
            )
        })

    return patents
LENS_PATENT_URL = "https://api.lens.org/patent"


def get_patent_details(lens_id: str):

    headers = {
        "Authorization": f"Bearer {LENS_API_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.get(
        f"{LENS_PATENT_URL}/{lens_id}",
        headers=headers
    )

    return response.json()
from app.models.patent_bookmark import PatentBookmark


def save_bookmark(db, user_id, bookmark_data):

    bookmark = PatentBookmark(
        user_id=user_id,
        lens_id=bookmark_data.lens_id,
        title=bookmark_data.title,
        applicant=bookmark_data.applicant,
        jurisdiction=bookmark_data.jurisdiction
    )

    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)

    return bookmark


def get_bookmarks(db, user_id):

    return (
        db.query(PatentBookmark)
        .filter(PatentBookmark.user_id == user_id)
        .all()
    )


def delete_bookmark(db, bookmark_id, user_id):

    bookmark = (
        db.query(PatentBookmark)
        .filter(
            PatentBookmark.id == bookmark_id,
            PatentBookmark.user_id == user_id
        )
        .first()
    )

    if not bookmark:
        return None

    db.delete(bookmark)
    db.commit()

    return {"message": "Bookmark deleted successfully"}
def get_similar_patents(lens_id: str, size: int = 5):

    # Get patent details
    patent = get_patent_details(lens_id)

    biblio = patent.get("biblio", {})

    # Extract English title
    title = ""

    titles = biblio.get("invention_title", [])

    for t in titles:
        if t.get("lang") == "en":
            title = t.get("text")
            break

    # If English title not available, use first title
    if not title and titles:
        title = titles[0].get("text", "")

    if not title:
        return []

    headers = {
        "Authorization": f"Bearer {LENS_API_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "query": {
            "match": {
                "title": title
            }
        },
        "size": size + 1
    }

    response = requests.post(
        LENS_SEARCH_URL,
        headers=headers,
        json=payload
    )

    data = response.json()

    patents = format_patents(data.get("data", []))

    # Remove the original patent
    patents = [
        patent for patent in patents
        if patent["lens_id"] != lens_id
    ]

    return patents[:size]
from collections import Counter


def get_patent_analytics(query: str, size: int = 100):

    response = search_patents(query, size)

    patents = format_patents(response.get("data", []))

    country_counter = Counter()
    legal_status_counter = Counter()
    year_counter = Counter()
    applicant_counter = Counter()
    inventor_counter = Counter()

    for patent in patents:

        # Country
        if patent["jurisdiction"]:
            country_counter[patent["jurisdiction"]] += 1

        # Legal Status
        if patent["legal_status"]:
            legal_status_counter[patent["legal_status"]] += 1

        # Publication Year
        if patent["publication_date"]:
            year = patent["publication_date"][:4]
            year_counter[year] += 1

        # Applicant
        if patent["applicant"]:
            applicant_counter[patent["applicant"]] += 1

        # Inventor
        if patent["inventor"]:
            inventor_counter[patent["inventor"]] += 1

    return {
        "total_patents": len(patents),
        "country_distribution": dict(country_counter),
        "legal_status_distribution": dict(legal_status_counter),
        "publication_year_distribution": dict(year_counter),
        "top_applicants": dict(applicant_counter.most_common(10)),
        "top_inventors": dict(inventor_counter.most_common(10))
    }
def compare_patents(lens_id_1: str, lens_id_2: str):

    patent1 = get_patent_details(lens_id_1)
    patent2 = get_patent_details(lens_id_2)

    def extract_data(patent):

        biblio = patent.get("biblio", {})

        title = ""
        if biblio.get("invention_title"):
            title = biblio["invention_title"][0].get("text", "")

        applicant = ""
        applicants = biblio.get("parties", {}).get("applicants", [])
        if applicants:
            applicant = applicants[0].get(
                "extracted_name", {}
            ).get("value", "")

        inventor = ""
        inventors = biblio.get("parties", {}).get("inventors", [])
        if inventors:
            inventor = inventors[0].get(
                "extracted_name", {}
            ).get("value", "")

        abstract = ""
        if patent.get("abstract"):
            abstract = patent["abstract"][0].get("text", "")

        return {
            "lens_id": patent.get("lens_id"),
            "title": title,
            "applicant": applicant,
            "inventor": inventor,
            "jurisdiction": patent.get("jurisdiction"),
            "publication_date": patent.get("date_published"),
            "legal_status": patent.get("legal_status", {}).get(
                "patent_status", ""
            ),
            "abstract": abstract
        }

    return {
        "patent_1": extract_data(patent1),
        "patent_2": extract_data(patent2)
    }
def get_patent_timeline(lens_id: str):

    patent = get_patent_details(lens_id)

    timeline = []

    # Application Date
    application = (
        patent.get("biblio", {})
        .get("application_reference", {})
    )

    if application:
        timeline.append({
            "event": "Application Filed",
            "date": application.get("date"),
            "country": application.get("jurisdiction"),
            "kind": application.get("kind")
        })

    # Publication Date
    publication = (
        patent.get("biblio", {})
        .get("publication_reference", {})
    )

    if publication:
        timeline.append({
            "event": "Publication",
            "date": publication.get("date"),
            "country": publication.get("jurisdiction"),
            "kind": publication.get("kind")
        })

    # Grant Date
    legal = patent.get("legal_status", {})

    if legal.get("grant_date"):
        timeline.append({
            "event": "Patent Granted",
            "date": legal.get("grant_date"),
            "country": patent.get("jurisdiction"),
            "kind": "Grant"
        })

    # Patent Family Members
    family = (
        patent.get("families", {})
        .get("simple_family", {})
        .get("members", [])
    )

    for member in family:

        document = member.get("document_id", {})

        timeline.append({
            "event": "Family Patent",
            "date": document.get("date"),
            "country": document.get("jurisdiction"),
            "kind": document.get("kind")
        })

    # Sort by date
    timeline.sort(key=lambda x: x["date"] or "")

    return {
        "lens_id": lens_id,
        "timeline": timeline
    }
def get_patent_ai_insights(lens_id: str):

    patent = get_patent_details(lens_id)

    biblio = patent.get("biblio", {})

    # Title
    title = ""
    if biblio.get("invention_title"):
        title = biblio["invention_title"][0].get("text", "")

    # Applicant
    applicant = ""
    applicants = biblio.get("parties", {}).get("applicants", [])
    if applicants:
        applicant = applicants[0].get(
            "extracted_name", {}
        ).get("value", "")

    # Inventor
    inventor = ""
    inventors = biblio.get("parties", {}).get("inventors", [])
    if inventors:
        inventor = inventors[0].get(
            "extracted_name", {}
        ).get("value", "")

    # Abstract
    abstract = ""
    if patent.get("abstract"):
        abstract = patent["abstract"][0].get("text", "")

    prompt = f"""
You are an expert Patent Analyst.

Analyze the following patent and return ONLY valid JSON.

Return this exact structure:

{{
    "summary": "",
    "technology_domain": "",
    "innovation_score": 0,
    "novelty_analysis": "",
    "commercialization_potential": "",
    "market_opportunities": [],
    "recommended_industries": [],
    "key_innovations": []
}}

Patent Title:
{title}

Applicant:
{applicant}

Inventor:
{inventor}

Abstract:
{abstract}
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )

    result = response.json()

    print(result)

    if "error" in result:
        return {
            "error": result["error"]
        }

    try:
        return json.loads(result["response"])
    except Exception:
        return {
            "ai_response": result.get("response", "")
        }