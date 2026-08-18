import os
from datetime import datetime, date
from typing import Any, Dict, List

import requests

from app.models.funding_bookmark import FundingBookmark


# ============================================================
# CONFIGURATION
# ============================================================

GRANTS_SEARCH_URL = "https://api.grants.gov/v1/api/search2"
GRANTS_DETAILS_URL = "https://api.grants.gov/v1/api/fetchOpportunity"

OLLAMA_URL = "http://localhost:11434/api/generate"

# You currently have qwen2.5:1.5b installed.
# You can override it using OLLAMA_MODEL in .env
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")

REQUEST_TIMEOUT = 30
OLLAMA_TIMEOUT = 120


# ============================================================
# COMMON HELPERS
# ============================================================

def _safe_string(value: Any, default: str = "") -> str:
    """
    Convert a value safely to string.
    """
    if value is None:
        return default

    if isinstance(value, str):
        return value.strip()

    return str(value)


def _extract_data(response: requests.Response) -> Dict[str, Any]:
    """
    Safely extract JSON data from a requests response.
    """

    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        raise Exception(
            f"External API returned HTTP {response.status_code}: "
            f"{response.text[:500]}"
        ) from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise Exception(
            "External API returned invalid JSON."
        ) from exc

    if not isinstance(data, dict):
        raise Exception("External API returned an unexpected response format.")

    return data


def _parse_date(value: Any):
    """
    Parse common Grants.gov date formats.
    """

    if not value:
        return None

    value = _safe_string(value)

    formats = [
        "%m/%d/%Y",
        "%Y-%m-%d",
        "%m/%d/%Y %H:%M:%S",
        "%b %d, %Y %I:%M:%S %p %Z",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue

    return None


# ============================================================
# FORMAT SEARCH RESULTS
# ============================================================

def format_funding(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert Grants.gov search results into the format
    used by the InnoBridge-AI application.
    """

    funding = []

    for item in results or []:

        if not isinstance(item, dict):
            continue

        # Grants.gov uses agencyName, not agency.
        agency = (
            item.get("agencyName")
            or item.get("agency")
            or item.get("agencyCode")
            or ""
        )

        close_date = (
            item.get("closeDate")
            or item.get("closingDate")
            or ""
        )

        open_date = (
            item.get("openDate")
            or item.get("openingDate")
            or ""
        )

        status = (
            item.get("oppStatus")
            or item.get("status")
            or ""
        )

        # Search2 normally doesn't provide award amounts.
        # Keep this field because FundingResult expects it.
        funding_amount = (
            item.get("fundingAmount")
            or item.get("awardAmount")
            or item.get("awardCeiling")
            or ""
        )

        funding.append(
            {
                "opportunity_id": _safe_string(
                    item.get("id")
                ),

                "opportunity_number": _safe_string(
                    item.get("number")
                ),

                "title": _safe_string(
                    item.get("title")
                ),

                "agency": _safe_string(
                    agency
                ),

                "open_date": _safe_string(
                    open_date
                ),

                "close_date": _safe_string(
                    close_date
                ),

                "funding_amount": _safe_string(
                    funding_amount,
                    "Not specified"
                ),

                "status": _safe_string(
                    status
                ),

                "agency_code": _safe_string(
                    item.get("agencyCode")
                ),

                "document_type": _safe_string(
                    item.get("docType")
                ),

                "aln": item.get("alnist", []),
            }
        )

    return funding


# ============================================================
# FUNDING SEARCH
# ============================================================

def search_funding(keyword: str):

    keyword = (keyword or "").strip()

    if not keyword:
        return {
            "count": 0,
            "results": [],
            "message": "Please provide a funding keyword."
        }

    payload = {
        "keyword": keyword,
        "rows": 20,
    }

    try:

        response = requests.post(
            GRANTS_SEARCH_URL,
            json=payload,
            headers={
                "Content-Type": "application/json"
            },
            timeout=REQUEST_TIMEOUT,
        )

        data = _extract_data(response)

        api_data = data.get("data", {})

        if not isinstance(api_data, dict):
            api_data = {}

        results = api_data.get("oppHits", [])

        formatted_results = format_funding(results)

        return {
            "count": api_data.get(
                "hitCount",
                len(formatted_results)
            ),
            "results": formatted_results,
        }

    except requests.exceptions.Timeout:
        return {
            "count": 0,
            "results": [],
            "error": "Grants.gov request timed out."
        }

    except requests.exceptions.ConnectionError:
        return {
            "count": 0,
            "results": [],
            "error": (
                "Could not connect to Grants.gov. "
                "Please check your internet connection."
            )
        }

    except Exception as exc:
        return {
            "count": 0,
            "results": [],
            "error": f"Funding search failed: {str(exc)}"
        }


# ============================================================
# FUNDING DETAILS
# ============================================================

def get_funding_details(opportunity_id: str):

    opportunity_id = _safe_string(opportunity_id)

    if not opportunity_id:
        return {
            "error": "Opportunity ID is required."
        }

    payload = {
        "opportunityId": opportunity_id
    }

    try:

        response = requests.post(
            GRANTS_DETAILS_URL,
            json=payload,
            headers={
                "Content-Type": "application/json"
            },
            timeout=REQUEST_TIMEOUT,
        )

        data = _extract_data(response)

        return data

    except requests.exceptions.Timeout:
        return {
            "error": "Grants.gov details request timed out."
        }

    except requests.exceptions.ConnectionError:
        return {
            "error": (
                "Could not connect to Grants.gov."
            )
        }

    except Exception as exc:
        return {
            "error": f"Unable to get funding details: {str(exc)}"
        }


# ============================================================
# BOOKMARK
# ============================================================

def save_funding_bookmark(
    db,
    user_id,
    bookmark_data
):

    existing = (
        db.query(FundingBookmark)
        .filter(
            FundingBookmark.user_id == user_id,
            FundingBookmark.opportunity_id
            == bookmark_data.opportunity_id
        )
        .first()
    )

    if existing:

        return {
            "message": "Funding opportunity already bookmarked.",
            "bookmark_id": existing.id,
        }

    bookmark = FundingBookmark(
        user_id=user_id,
        opportunity_id=bookmark_data.opportunity_id,
        opportunity_number=bookmark_data.opportunity_number,
        title=bookmark_data.title,
        agency=bookmark_data.agency,
        close_date=bookmark_data.close_date,
    )

    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)

    return {
        "message": "Funding opportunity bookmarked successfully.",
        "bookmark_id": bookmark.id,
        "opportunity_id": bookmark.opportunity_id,
        "title": bookmark.title,
    }


# ============================================================
# GET BOOKMARKS
# ============================================================

def get_funding_bookmarks(db, user_id):

    bookmarks = (
        db.query(FundingBookmark)
        .filter(
            FundingBookmark.user_id == user_id
        )
        .order_by(
            FundingBookmark.created_at.desc()
        )
        .all()
    )

    return {
        "count": len(bookmarks),
        "bookmarks": [
            {
                "id": bookmark.id,
                "opportunity_id": bookmark.opportunity_id,
                "opportunity_number": bookmark.opportunity_number,
                "title": bookmark.title,
                "agency": bookmark.agency,
                "close_date": bookmark.close_date,
                "created_at": (
                    bookmark.created_at.isoformat()
                    if bookmark.created_at
                    else None
                ),
            }
            for bookmark in bookmarks
        ]
    }


# ============================================================
# DELETE BOOKMARK
# ============================================================

def delete_funding_bookmark(
    db,
    bookmark_id,
    user_id
):

    bookmark = (
        db.query(FundingBookmark)
        .filter(
            FundingBookmark.id == bookmark_id,
            FundingBookmark.user_id == user_id,
        )
        .first()
    )

    if not bookmark:

        return {
            "success": False,
            "message": "Funding bookmark not found."
        }

    db.delete(bookmark)
    db.commit()

    return {
        "success": True,
        "message": "Funding bookmark deleted successfully."
    }


# ============================================================
# ANALYTICS
# ============================================================

def get_funding_analytics(
    keyword: str,
    size: int = 100
):

    size = max(1, min(size, 100))

    data = search_funding(keyword)

    opportunities = data.get(
        "results",
        []
    )

    opportunities = opportunities[:size]

    if not opportunities:

        return {
            "keyword": keyword,
            "total_opportunities": 0,
            "agencies": {},
            "open_opportunities": 0,
            "closed_opportunities": 0,
            "upcoming_deadlines": 0,
        }

    agencies = {}

    open_count = 0
    closed_count = 0
    upcoming_count = 0

    today = date.today()

    for opportunity in opportunities:

        agency = (
            opportunity.get("agency")
            or "Unknown"
        )

        agencies[agency] = (
            agencies.get(agency, 0) + 1
        )

        status = (
            opportunity.get("status")
            or ""
        ).lower()

        close_date = opportunity.get(
            "close_date"
        )

        parsed_close = _parse_date(
            close_date
        )

        if status in {
            "closed",
            "archived"
        }:

            closed_count += 1

        elif parsed_close:

            if parsed_close < today:
                closed_count += 1
            else:
                open_count += 1
                upcoming_count += 1

        else:

            open_count += 1

    return {
        "keyword": keyword,
        "total_opportunities": len(opportunities),
        "agencies": agencies,
        "open_opportunities": open_count,
        "closed_opportunities": closed_count,
        "upcoming_deadlines": upcoming_count,
    }


# ============================================================
# OLLAMA HELPER
# ============================================================

def _generate_with_ollama(
    prompt: str,
    timeout: int = OLLAMA_TIMEOUT
):

    try:

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
            },
            timeout=timeout,
        )

        if response.status_code != 200:

            return {
                "success": False,
                "error": (
                    f"Ollama returned HTTP "
                    f"{response.status_code}: "
                    f"{response.text[:500]}"
                )
            }

        data = response.json()

        ai_response = data.get(
            "response",
            ""
        )

        if not ai_response:

            return {
                "success": False,
                "error": "Ollama returned an empty response."
            }

        return {
            "success": True,
            "response": ai_response.strip()
        }

    except requests.exceptions.ConnectionError:

        return {
            "success": False,
            "error": (
                "Ollama is not running. "
                "Start Ollama and try again."
            )
        }

    except requests.exceptions.Timeout:

        return {
            "success": False,
            "error": (
                "Ollama request timed out."
            )
        }

    except Exception as exc:

        return {
            "success": False,
            "error": f"Ollama error: {str(exc)}"
        }


# ============================================================
# AI FUNDING INSIGHTS
# ============================================================

def get_funding_ai_insights(
    opportunity_id: str
):

    funding = get_funding_details(
        opportunity_id
    )

    if not funding or funding.get("error"):

        return {
            "opportunity_id": opportunity_id,
            "error": (
                funding.get("error")
                if isinstance(funding, dict)
                else "Funding opportunity not found."
            )
        }

    prompt = f"""
You are an expert research funding advisor.

Analyze the following Grants.gov funding opportunity.

FUNDING OPPORTUNITY:
{funding}

Provide a practical analysis using exactly these sections:

1. Summary
2. Main Objectives
3. Eligibility
4. Important Requirements
5. Potential Applicant Fit
6. Recommended Action

Important rules:
- Use only information present in the funding opportunity.
- Do not invent eligibility requirements.
- Do not invent deadlines.
- Do not invent funding amounts.
- If information is missing, clearly say "Not specified in the available data".
- Keep the explanation clear and practical.
"""

    result = _generate_with_ollama(
        prompt
    )

    if not result["success"]:

        return {
            "opportunity_id": opportunity_id,
            "error": result["error"]
        }

    return {
        "opportunity_id": opportunity_id,
        "ai_insights": result["response"]
    }


# ============================================================
# GENERATE FUNDING PROPOSAL
# ============================================================

def generate_funding_proposal(
    opportunity_id: str,
    project_title: str,
    project_description: str,
    organization_name: str
):

    funding = get_funding_details(
        opportunity_id
    )

    if not funding or funding.get("error"):

        return {
            "opportunity_id": opportunity_id,
            "error": (
                funding.get("error")
                if isinstance(funding, dict)
                else "Funding opportunity not found."
            )
        }

    prompt = f"""
You are an expert government funding proposal writer.

FUNDING OPPORTUNITY:
{funding}

PROJECT TITLE:
{project_title}

PROJECT DESCRIPTION:
{project_description}

ORGANIZATION:
{organization_name}

Create a professional draft funding proposal.

Use these sections:

1. Executive Summary
2. Problem Statement
3. Proposed Solution
4. Objectives
5. Methodology
6. Expected Outcomes
7. Innovation
8. Project Impact
9. Conclusion

Rules:
- Make the proposal relevant to the funding opportunity.
- Do not invent eligibility rules.
- Do not invent funding amounts.
- Do not invent deadlines.
- Do not claim that the organization is eligible unless the provided data supports it.
- Clearly identify information that requires verification.
"""

    result = _generate_with_ollama(
        prompt,
        timeout=180
    )

    if not result["success"]:

        return {
            "opportunity_id": opportunity_id,
            "error": result["error"]
        }

    return {
        "opportunity_id": opportunity_id,
        "project_title": project_title,
        "organization_name": organization_name,
        "proposal": result["response"]
    }


# ============================================================
# FUNDING RECOMMENDATIONS
# ============================================================

def get_funding_recommendations(
    project_title: str,
    project_description: str,
    keyword: str,
    size: int = 20
):

    size = max(1, min(size, 100))

    data = search_funding(
        keyword
    )

    opportunities = data.get(
        "results",
        []
    )

    opportunities = opportunities[:size]

    if not opportunities:

        return {
            "project_title": project_title,
            "recommendations": []
        }

    project_text = (
        f"{project_title} "
        f"{project_description}"
    ).lower()

    stop_words = {
        "the",
        "and",
        "for",
        "with",
        "from",
        "this",
        "that",
        "are",
        "is",
        "an",
        "of",
        "to",
        "in",
        "on",
        "a",
        "using",
        "use",
        "based",
        "into",
        "will",
        "can",
        "our",
        "their",
    }

    project_words = {
        word.strip(".,!?()[]{}:;")
        for word in project_text.split()
        if len(word.strip(".,!?()[]{}:;")) > 2
        and word.strip(".,!?()[]{}:;")
        not in stop_words
    }

    recommendations = []

    for opportunity in opportunities:

        title = _safe_string(
            opportunity.get("title")
        )

        agency = _safe_string(
            opportunity.get("agency")
        )

        funding_text = (
            f"{title} {agency}"
        ).lower()

        funding_words = {
            word.strip(".,!?()[]{}:;")
            for word in funding_text.split()
            if len(word.strip(".,!?()[]{}:;")) > 2
        }

        matching_words = (
            project_words &
            funding_words
        )

        if project_words:

            score = (
                len(matching_words)
                / len(project_words)
            ) * 100

        else:

            score = 0

        recommendations.append(
            {
                "opportunity_id": opportunity.get(
                    "opportunity_id"
                ),

                "opportunity_number": opportunity.get(
                    "opportunity_number"
                ),

                "title": title,

                "agency": agency,

                "close_date": opportunity.get(
                    "close_date"
                ),

                "match_score": round(
                    score,
                    2
                ),

                "matching_keywords": sorted(
                    list(matching_words)
                ),
            }
        )

    recommendations.sort(
        key=lambda item: item["match_score"],
        reverse=True
    )

    return {
        "project_title": project_title,
        "recommendations": recommendations
    }


# ============================================================
# FUNDING DEADLINES
# ============================================================

def get_funding_deadlines(
    keyword: str,
    size: int = 20
):

    size = max(1, min(size, 100))

    data = search_funding(
        keyword
    )

    opportunities = data.get(
        "results",
        []
    )

    opportunities = opportunities[:size]

    deadlines = []

    today = date.today()

    for opportunity in opportunities:

        close_date = opportunity.get(
            "close_date"
        )

        if not close_date:
            continue

        deadline = _parse_date(
            close_date
        )

        if not deadline:
            continue

        days_remaining = (
            deadline - today
        ).days

        if days_remaining < 0:
            continue

        if days_remaining <= 7:

            urgency = "URGENT"

        elif days_remaining <= 30:

            urgency = "UPCOMING"

        else:

            urgency = "LATER"

        deadlines.append(
            {
                "opportunity_id": opportunity.get(
                    "opportunity_id"
                ),

                "opportunity_number": opportunity.get(
                    "opportunity_number"
                ),

                "title": opportunity.get(
                    "title"
                ),

                "agency": opportunity.get(
                    "agency"
                ),

                "close_date": close_date,

                "days_remaining": days_remaining,

                "urgency": urgency,
            }
        )

    deadlines.sort(
        key=lambda item: item["days_remaining"]
    )

    return {
        "keyword": keyword,
        "total_upcoming": len(deadlines),
        "deadlines": deadlines,
    }