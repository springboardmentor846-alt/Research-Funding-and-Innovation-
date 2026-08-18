import os
import json
import requests
from collections import Counter
from dotenv import load_dotenv

from app.models.patent_bookmark import PatentBookmark


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

LENS_API_TOKEN = os.getenv("LENS_API_TOKEN")

USE_MOCK_PATENTS = (
    os.getenv("USE_MOCK_PATENTS", "true").lower()
    == "true"
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen2.5:1.5b"
)

LENS_SEARCH_URL = "https://api.lens.org/patent/search"
LENS_PATENT_URL = "https://api.lens.org/patent"

OLLAMA_URL = "http://localhost:11434/api/generate"


# ============================================================
# MOCK PATENT DATA
# ============================================================

MOCK_PATENTS = [
    {
        "lens_id": "MOCK-001",
        "title": "Artificial Intelligence Based Medical Diagnosis System",
        "applicant": "InnoHealth Technologies",
        "inventor": "Ananya Sharma",
        "publication_date": "2024-02-15",
        "jurisdiction": "IN",
        "legal_status": "Active",
        "abstract": (
            "A computer-based artificial intelligence system "
            "for assisting medical diagnosis using machine "
            "learning models and clinical data."
        ),
    },
    {
        "lens_id": "MOCK-002",
        "title": "Machine Learning System for Predictive Healthcare",
        "applicant": "HealthAI Research Labs",
        "inventor": "Rahul Kumar",
        "publication_date": "2023-08-20",
        "jurisdiction": "US",
        "legal_status": "Active",
        "abstract": (
            "A predictive healthcare platform using machine "
            "learning to identify potential health risks "
            "from patient data."
        ),
    },
    {
        "lens_id": "MOCK-003",
        "title": "Deep Learning Based Disease Detection Platform",
        "applicant": "VisionMed Innovations",
        "inventor": "Priya Nair",
        "publication_date": "2022-11-10",
        "jurisdiction": "EP",
        "legal_status": "Granted",
        "abstract": (
            "A deep learning platform for detecting diseases "
            "from medical images."
        ),
    },
    {
        "lens_id": "MOCK-004",
        "title": "AI Powered Drug Discovery Platform",
        "applicant": "BioTech Intelligence",
        "inventor": "Arjun Menon",
        "publication_date": "2024-05-12",
        "jurisdiction": "IN",
        "legal_status": "Pending",
        "abstract": (
            "An artificial intelligence platform for identifying "
            "potential drug candidates and predicting molecular "
            "properties."
        ),
    },
    {
        "lens_id": "MOCK-005",
        "title": "Intelligent Healthcare Decision Support System",
        "applicant": "Digital Health Systems",
        "inventor": "Meera Iyer",
        "publication_date": "2021-06-25",
        "jurisdiction": "US",
        "legal_status": "Active",
        "abstract": (
            "A decision support system that combines artificial "
            "intelligence and clinical information to support "
            "healthcare professionals."
        ),
    },
    {
        "lens_id": "MOCK-006",
        "title": "Computer Vision Based Medical Image Analysis",
        "applicant": "MedVision AI",
        "inventor": "Karthik Rao",
        "publication_date": "2023-03-18",
        "jurisdiction": "IN",
        "legal_status": "Granted",
        "abstract": (
            "A computer vision system for automated analysis "
            "of medical images using deep neural networks."
        ),
    },
    {
        "lens_id": "MOCK-007",
        "title": "Natural Language Processing Healthcare Assistant",
        "applicant": "CareAI Systems",
        "inventor": "Sneha Patel",
        "publication_date": "2024-01-30",
        "jurisdiction": "GB",
        "legal_status": "Pending",
        "abstract": (
            "An intelligent healthcare assistant using natural "
            "language processing to answer healthcare-related "
            "questions."
        ),
    },
    {
        "lens_id": "MOCK-008",
        "title": "Federated Learning System for Secure Medical Data",
        "applicant": "SecureHealth Labs",
        "inventor": "Vikram Singh",
        "publication_date": "2022-09-05",
        "jurisdiction": "IN",
        "legal_status": "Active",
        "abstract": (
            "A federated learning architecture that allows "
            "machine learning models to be trained using "
            "distributed healthcare data without centralizing "
            "sensitive information."
        ),
    },
]


# ============================================================
# HELPERS
# ============================================================

def safe_text(value):
    if value is None:
        return ""

    if isinstance(value, str):
        return value

    return str(value)


def find_mock_patent(lens_id):
    for patent in MOCK_PATENTS:
        if patent["lens_id"] == lens_id:
            return patent

    return None


def search_mock_patents(query, size=10):

    query = query.lower().strip()

    if not query:
        return MOCK_PATENTS[:size]

    words = query.split()

    matches = []

    for patent in MOCK_PATENTS:

        searchable_text = (
            patent["title"]
            + " "
            + patent["applicant"]
            + " "
            + patent["inventor"]
            + " "
            + patent["abstract"]
        ).lower()

        score = sum(
            1 for word in words
            if word in searchable_text
        )

        if score > 0:
            matches.append(
                (score, patent)
            )

    matches.sort(
        key=lambda x: x[0],
        reverse=True
    )

    return [
        patent
        for _, patent in matches[:size]
    ]


# ============================================================
# LENS HEADERS
# ============================================================

def lens_headers():

    if not LENS_API_TOKEN:
        raise Exception(
            "LENS_API_TOKEN is not configured."
        )

    return {
        "Authorization": f"Bearer {LENS_API_TOKEN}",
        "Content-Type": "application/json",
    }


# ============================================================
# PATENT SEARCH
# ============================================================

def search_patents(query, size=10):

    # Development mode
    if USE_MOCK_PATENTS:

        return {
            "data": search_mock_patents(
                query,
                size
            ),
            "mock": True,
        }

    # Real Lens API
    payload = {
        "query": {
            "match": {
                "title": query
            }
        },
        "size": size,
    }

    try:

        response = requests.post(
            LENS_SEARCH_URL,
            json=payload,
            headers=lens_headers(),
            timeout=30,
        )

        if response.status_code == 401:

            raise Exception(
                "Lens API authentication failed. "
                "Your Lens API access may be expired."
            )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:

        raise Exception(
            f"Lens API request failed: {str(e)}"
        )


# ============================================================
# FORMAT PATENTS
# ============================================================

def format_patents(results):

    formatted = []

    if not isinstance(results, list):
        return formatted

    for item in results:

        # Mock data
        if item.get("lens_id", "").startswith("MOCK-"):

            formatted.append({
                "lens_id": item["lens_id"],
                "title": item["title"],
                "applicant": item["applicant"],
                "inventor": item["inventor"],
                "publication_date": item["publication_date"],
                "jurisdiction": item["jurisdiction"],
                "legal_status": item["legal_status"],
            })

            continue

        # Real Lens data
        biblio = item.get(
            "biblio",
            {}
        )

        if not isinstance(biblio, dict):
            biblio = {}

        title = ""

        invention_title = biblio.get(
            "invention_title",
            []
        )

        if invention_title:

            first_title = invention_title[0]

            if isinstance(
                first_title,
                dict
            ):
                title = safe_text(
                    first_title.get("text")
                )
            else:
                title = safe_text(
                    first_title
                )

        parties = biblio.get(
            "parties",
            {}
        )

        if not isinstance(parties, dict):
            parties = {}

        applicants = parties.get(
            "applicants",
            []
        )

        inventors = parties.get(
            "inventors",
            []
        )

        applicant = ""

        if applicants:

            applicant_data = applicants[0]

            if isinstance(
                applicant_data,
                dict
            ):

                extracted = applicant_data.get(
                    "extracted_name",
                    {}
                )

                if isinstance(
                    extracted,
                    dict
                ):
                    applicant = safe_text(
                        extracted.get("value")
                    )

        inventor = ""

        if inventors:

            inventor_data = inventors[0]

            if isinstance(
                inventor_data,
                dict
            ):

                extracted = inventor_data.get(
                    "extracted_name",
                    {}
                )

                if isinstance(
                    extracted,
                    dict
                ):
                    inventor = safe_text(
                        extracted.get("value")
                    )

        legal_status = item.get(
            "legal_status",
            {}
        )

        if not isinstance(
            legal_status,
            dict
        ):
            legal_status = {}

        formatted.append({

            "lens_id": safe_text(
                item.get("lens_id")
            ),

            "title": title,

            "applicant": applicant,

            "inventor": inventor,

            "publication_date": safe_text(
                item.get("date_published")
            ),

            "jurisdiction": safe_text(
                item.get("jurisdiction")
            ),

            "legal_status": safe_text(
                legal_status.get(
                    "patent_status"
                )
            ),
        })

    return formatted


# ============================================================
# PATENT DETAILS
# ============================================================

def get_patent_details(lens_id):

    # Mock
    if USE_MOCK_PATENTS:

        patent = find_mock_patent(
            lens_id
        )

        if not patent:
            raise Exception(
                "Patent not found."
            )

        return {
            "lens_id": patent["lens_id"],
            "title": patent["title"],
            "applicant": patent["applicant"],
            "inventor": patent["inventor"],
            "publication_date": patent["publication_date"],
            "jurisdiction": patent["jurisdiction"],
            "legal_status": patent["legal_status"],
            "abstract": patent["abstract"],
        }

    # Lens
    try:

        response = requests.get(
            f"{LENS_PATENT_URL}/{lens_id}",
            headers=lens_headers(),
            timeout=30,
        )

        if response.status_code == 401:
            raise Exception(
                "Lens API authentication failed."
            )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:

        raise Exception(
            f"Unable to retrieve patent: {str(e)}"
        )


# ============================================================
# SIMILAR PATENTS
# ============================================================

def get_similar_patents(lens_id):

    patent = get_patent_details(
        lens_id
    )

    # Mock
    if USE_MOCK_PATENTS:

        title = patent.get(
            "title",
            ""
        ).lower()

        words = set(
            title.split()
        )

        results = []

        for item in MOCK_PATENTS:

            if item["lens_id"] == lens_id:
                continue

            item_words = set(
                item["title"].lower().split()
            )

            similarity = len(
                words.intersection(
                    item_words
                )
            )

            if similarity > 0:

                results.append(
                    item
                )

        # If no keyword similarity,
        # still return useful patents.
        if not results:

            results = [
                item
                for item in MOCK_PATENTS
                if item["lens_id"] != lens_id
            ]

        return [
            {
                "lens_id": item["lens_id"],
                "title": item["title"],
                "applicant": item["applicant"],
                "publication_date": item[
                    "publication_date"
                ],
                "jurisdiction": item[
                    "jurisdiction"
                ],
            }
            for item in results[:5]
        ]

    # Real Lens mode
    title = patent.get(
        "biblio",
        {}
    ).get(
        "invention_title",
        [{}]
    )[0].get(
        "text",
        ""
    )

    payload = {
        "query": {
            "match": {
                "title": title
            }
        },
        "size": 6,
    }

    response = requests.post(
        LENS_SEARCH_URL,
        json=payload,
        headers=lens_headers(),
        timeout=30,
    )

    response.raise_for_status()

    results = format_patents(
        response.json().get(
            "data",
            []
        )
    )

    return [
        item
        for item in results
        if item["lens_id"] != lens_id
    ][:5]


# ============================================================
# BOOKMARK
# ============================================================

def save_bookmark(
    db,
    user_id,
    bookmark_data
):

    existing = (
        db.query(PatentBookmark)
        .filter(
            PatentBookmark.user_id == user_id,
            PatentBookmark.lens_id
            == bookmark_data.lens_id,
        )
        .first()
    )

    if existing:

        return {
            "message":
                "Patent already bookmarked.",
            "bookmark_id":
                existing.id,
        }

    bookmark = PatentBookmark(

        user_id=user_id,

        lens_id=bookmark_data.lens_id,

        title=bookmark_data.title,

        applicant=bookmark_data.applicant,

        jurisdiction=bookmark_data.jurisdiction,
    )

    db.add(bookmark)

    db.commit()

    db.refresh(bookmark)

    return {
        "message":
            "Patent bookmarked successfully.",
        "bookmark_id":
            bookmark.id,
        "lens_id":
            bookmark.lens_id,
        "title":
            bookmark.title,
    }


# ============================================================
# GET BOOKMARKS
# ============================================================

def get_bookmarks(
    db,
    user_id
):

    return (
        db.query(PatentBookmark)
        .filter(
            PatentBookmark.user_id == user_id
        )
        .order_by(
            PatentBookmark.bookmarked_at.desc()
        )
        .all()
    )


# ============================================================
# DELETE BOOKMARK
# ============================================================

def delete_bookmark(
    db,
    bookmark_id,
    user_id
):

    bookmark = (
        db.query(PatentBookmark)
        .filter(
            PatentBookmark.id == bookmark_id,
            PatentBookmark.user_id == user_id,
        )
        .first()
    )

    if not bookmark:

        return {
            "message":
                "Bookmark not found."
        }

    db.delete(bookmark)

    db.commit()

    return {
        "message":
            "Bookmark removed successfully."
    }


# ============================================================
# ANALYTICS
# ============================================================

def get_patent_analytics(
    query,
    size=100
):

    response = search_patents(
        query,
        size
    )

    patents = format_patents(
        response.get(
            "data",
            []
        )
    )

    jurisdictions = Counter()

    legal_statuses = Counter()

    years = Counter()

    applicants = Counter()

    inventors = Counter()

    for patent in patents:

        jurisdiction = patent.get(
            "jurisdiction"
        )

        if jurisdiction:
            jurisdictions[
                jurisdiction
            ] += 1

        status = patent.get(
            "legal_status"
        )

        if status:
            legal_statuses[
                status
            ] += 1

        date = patent.get(
            "publication_date"
        )

        if date:

            year = date[:4]

            if year:
                years[year] += 1

        applicant = patent.get(
            "applicant"
        )

        if applicant:
            applicants[
                applicant
            ] += 1

        inventor = patent.get(
            "inventor"
        )

        if inventor:
            inventors[
                inventor
            ] += 1

    return {

        "total_patents":
            len(patents),

        "jurisdiction_distribution":
            dict(jurisdictions),

        "legal_status_distribution":
            dict(legal_statuses),

        "publication_year_distribution":
            dict(years),

        "top_applicants":
            dict(
                applicants.most_common(10)
            ),

        "top_inventors":
            dict(
                inventors.most_common(10)
            ),
    }


# ============================================================
# COMPARISON
# ============================================================

def compare_patents(
    lens_id_1,
    lens_id_2
):

    patent1 = get_patent_details(
        lens_id_1
    )

    patent2 = get_patent_details(
        lens_id_2
    )

    return {
        "patent_1": patent1,
        "patent_2": patent2,
    }


# ============================================================
# TIMELINE
# ============================================================

def get_patent_timeline(
    lens_id
):

    patent = get_patent_details(
        lens_id
    )

    publication_date = patent.get(
        "publication_date",
        ""
    )

    return {

        "lens_id":
            lens_id,

        "timeline": [

            {
                "event":
                    "Patent Publication",

                "date":
                    publication_date,

                "description":
                    "Patent was published."
            },

            {
                "event":
                    "Patent Analysis",

                "date":
                    publication_date,

                "description":
                    "Patent is available for innovation analysis."
            }
        ]
    }


# ============================================================
# AI INSIGHTS
# ============================================================

def get_patent_ai_insights(
    lens_id
):

    patent = get_patent_details(
        lens_id
    )

    title = patent.get(
        "title",
        ""
    )

    abstract = patent.get(
        "abstract",
        ""
    )

    applicant = patent.get(
        "applicant",
        ""
    )

    prompt = f"""
You are a patent intelligence analyst.

Analyze this patent.

Title:
{title}

Applicant:
{applicant}

Abstract:
{abstract}

Return ONLY JSON in exactly this structure:

{{
    "summary": "string",
    "technology_domain": "string",
    "innovation_score": 0,
    "novelty_analysis": "string",
    "commercialization_potential": "string",
    "market_opportunities": [],
    "recommended_industries": [],
    "key_innovations": []
}}

innovation_score must be between 0 and 100.

All array fields must contain strings.
"""

    try:

        response = requests.post(

            OLLAMA_URL,

            json={

                "model":
                    OLLAMA_MODEL,

                "prompt":
                    prompt,

                "stream":
                    False,

                "options": {
                    "temperature": 0.2
                }
            },

            timeout=120
        )

        response.raise_for_status()

        raw = response.json().get(
            "response",
            ""
        )

        # Remove Markdown fences
        raw = raw.replace(
            "```json",
            ""
        ).replace(
            "```",
            ""
        ).strip()

        try:

            result = json.loads(raw)

        except json.JSONDecodeError:

            result = {
                "summary": raw,
                "technology_domain":
                    "Artificial Intelligence",
                "innovation_score": 70,
                "novelty_analysis":
                    "AI-generated analysis requires further patent review.",
                "commercialization_potential":
                    "Potential commercial applications should be evaluated.",
                "market_opportunities": [],
                "recommended_industries": [],
                "key_innovations": [],
            }

        # Ensure all fields exist
        result.setdefault(
            "summary",
            ""
        )

        result.setdefault(
            "technology_domain",
            ""
        )

        result.setdefault(
            "innovation_score",
            0
        )

        result.setdefault(
            "novelty_analysis",
            ""
        )

        result.setdefault(
            "commercialization_potential",
            ""
        )

        result.setdefault(
            "market_opportunities",
            []
        )

        result.setdefault(
            "recommended_industries",
            []
        )

        result.setdefault(
            "key_innovations",
            []
        )

        return result

    except requests.exceptions.RequestException:

        # Ollama unavailable:
        # still return useful development response.

        return {

            "summary":
                "AI analysis is temporarily unavailable. "
                "The patent data was retrieved successfully.",

            "technology_domain":
                "Artificial Intelligence",

            "innovation_score":
                0,

            "novelty_analysis":
                "AI analysis unavailable.",

            "commercialization_potential":
                "AI analysis unavailable.",

            "market_opportunities":
                [],

            "recommended_industries":
                [],

            "key_innovations":
                []
        }