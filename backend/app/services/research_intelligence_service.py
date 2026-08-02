import requests
from fastapi import HTTPException
from app.services.ollama_service import (
    summarize_research,
    generate_innovation,
    detect_research_gap,
    generate_literature_review,
    analyze_research_trends,
    generate_citations, research_chat,compare_research_papers,generate_research_proposal,check_novelty,
    generate_research_questions,recommend_methodology
)
OPENALEX_BASE_URL = "https://api.openalex.org/works"
INSTITUTIONS_BASE_URL = "https://api.openalex.org/institutions"

def search_papers(query: str, page: int = 1, per_page: int = 10):
    """
    Search research papers using the OpenAlex API.
    """

    params = {
        "search": query,
        "page": page,
        "per-page": per_page,
    }

    try:
        response = requests.get(
            OPENALEX_BASE_URL,
            params=params,
            timeout=15
        )

        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"OpenAlex API Error: {str(e)}"
        )

    data = response.json()

    papers = []

    for work in data.get("results", []):

        authors = []

        for authorship in work.get("authorships", []):

            author = authorship.get("author")

            if author:
                authors.append(
                    {
                        "name": author.get(
                            "display_name",
                            "Unknown"
                        )
                    }
                )

        papers.append(
            {
                "id": work.get("id"),
                "title": work.get("display_name"),
                "publication_year": work.get("publication_year"),
                "doi": work.get("doi"),
                "cited_by_count": work.get(
                    "cited_by_count",
                    0
                ),
                "authors": authors,
            }
        )

    return {
        "count": data.get("meta", {}).get(
            "count",
            0
        ),
        "results": papers,
    }


def get_paper_details(paper_id: str):
    """
    Get complete details of a research paper.
    """

    url = f"{OPENALEX_BASE_URL}/{paper_id}"

    try:
        response = requests.get(
            url,
            timeout=15
        )

        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"OpenAlex API Error: {str(e)}"
        )

    work = response.json()

    authors = []
    institutions = []

    for authorship in work.get("authorships", []):

        author = authorship.get("author")

        if author:
            authors.append(
                {
                    "name": author.get(
                        "display_name",
                        "Unknown"
                    )
                }
            )

        for institution in authorship.get("institutions", []):

            institutions.append(
                {
                    "name": institution.get(
                        "display_name",
                        "Unknown"
                    )
                }
            )

    journal = None

    if work.get("primary_location"):
        source = work["primary_location"].get("source")

        if source:
            journal = source.get("display_name")

    pdf_url = None

    if work.get("primary_location"):
        pdf_url = work["primary_location"].get("pdf_url")

    return {
        "id": work.get("id"),
        "title": work.get("display_name"),
        "publication_year": work.get("publication_year"),
        "doi": work.get("doi"),
        "cited_by_count": work.get(
            "cited_by_count",
            0
        ),
        "abstract": None,
        "journal": journal,
        "pdf_url": pdf_url,
        "authors": authors,
        "institutions": institutions,
    }
AUTHORS_BASE_URL = "https://api.openalex.org/authors"


def search_authors(query: str, page: int = 1, per_page: int = 10):
    """
    Search authors using the OpenAlex API.
    """

    params = {
        "search": query,
        "page": page,
        "per-page": per_page,
    }

    try:
        response = requests.get(
            AUTHORS_BASE_URL,
            params=params,
            timeout=15
        )

        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"OpenAlex API Error: {str(e)}"
        )

    data = response.json()

    authors = []

    for item in data.get("results", []):

        institution = None

        if item.get("last_known_institutions"):

            institutions = item.get("last_known_institutions")

            if institutions:
                institution = institutions[0].get("display_name")

        summary = item.get("summary_stats", {})

        authors.append(
            {
                "id": item.get("id"),
                "name": item.get("display_name"),
                "orcid": item.get("orcid"),
                "works_count": item.get("works_count", 0),
                "cited_by_count": item.get("cited_by_count", 0),
                "h_index": summary.get("h_index"),
                "last_known_institution": institution,
            }
        )

    return {
        "count": data.get("meta", {}).get("count", 0),
        "results": authors,
    }
def get_author_details(author_id: str):
    """
    Get complete details of an author.
    """

    url = f"{AUTHORS_BASE_URL}/{author_id}"

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"OpenAlex API Error: {str(e)}"
        )

    data = response.json()

    summary = data.get("summary_stats", {})

    institution = None
    country = None

    institutions = data.get("last_known_institutions", [])

    if institutions:
        institution = institutions[0].get("display_name")
        country = institutions[0].get("country_code")

    topics = []

    for topic in data.get("x_concepts", [])[:10]:

        topics.append(
            {
                "name": topic.get("display_name"),
                "count": topic.get("score", 0)
            }
        )

    return {
        "id": data.get("id"),
        "name": data.get("display_name"),
        "orcid": data.get("orcid"),
        "works_count": data.get("works_count", 0),
        "cited_by_count": data.get("cited_by_count", 0),
        "h_index": summary.get("h_index"),
        "institution": institution,
        "country": country,
        "topics": topics,
    }
def search_institutions(query: str, page: int = 1, per_page: int = 10):
    """
    Search research institutions using OpenAlex.
    """

    params = {
        "search": query,
        "page": page,
        "per-page": per_page,
    }

    try:
        response = requests.get(
            INSTITUTIONS_BASE_URL,
            params=params,
            timeout=15,
        )
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"OpenAlex API Error: {str(e)}"
        )

    data = response.json()

    institutions = []

    for item in data.get("results", []):

        institutions.append(
            {
                "id": item.get("id"),
                "name": item.get("display_name"),
                "country": item.get("country_code"),
                "works_count": item.get("works_count", 0),
                "cited_by_count": item.get("cited_by_count", 0),
            }
        )

    return {
        "count": data.get("meta", {}).get("count", 0),
        "results": institutions,
    }
def get_institution_details(institution_id: str):
    """
    Get complete details of an institution.
    """

    url = f"{INSTITUTIONS_BASE_URL}/{institution_id}"

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"OpenAlex API Error: {str(e)}"
        )

    data = response.json()

    topics = []

    for topic in data.get("x_concepts", [])[:10]:
        topics.append(
            {
                "name": topic.get("display_name"),
                "count": topic.get("score", 0.0)
            }
        )

    authors = []

    for author in data.get("associated_institutions", [])[:10]:
        authors.append(
            {
                "name": author.get("display_name")
            }
        )

    return {
        "id": data.get("id"),
        "name": data.get("display_name"),
        "country": data.get("country_code"),
        "homepage_url": data.get("homepage_url"),
        "works_count": data.get("works_count", 0),
        "cited_by_count": data.get("cited_by_count", 0),
        "topics": topics,
        "top_authors": authors,
    }
def get_recommendations(query: str, limit: int = 10):
    """
    Get research recommendations based on a query.
    """

    params = {
        "search": query,
        "per-page": limit,
        "sort": "cited_by_count:desc",
    }

    try:
        response = requests.get(
            OPENALEX_BASE_URL,
            params=params,
            timeout=15,
        )
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"OpenAlex API Error: {str(e)}"
        )

    data = response.json()

    recommendations = []

    for work in data.get("results", []):

        authors = []

        for authorship in work.get("authorships", []):
            author = authorship.get("author")
            if author:
                authors.append(author.get("display_name"))

        recommendations.append(
            {
                "title": work.get("display_name"),
                "authors": authors,
                "publication_year": work.get("publication_year"),
                "cited_by_count": work.get("cited_by_count", 0),
                "doi": work.get("doi"),
                "url": work.get("id"),
            }
        )

    return {
        "query": query,
        "recommendations": recommendations,
    }
def generate_research_summary(title: str, abstract: str):
    """
    Generate an AI-powered summary for a research paper.
    """

    return summarize_research(title, abstract)
# ============================================
# AI Innovation Generator
# ============================================

def generate_research_innovation(title: str, abstract: str):
    """
    Generate startup, product, business,
    patent and commercialization ideas
    from a research paper.
    """
    return generate_innovation(title, abstract)
def detect_research_gap_service(title: str, abstract: str):
    """
    Detect research gaps using Ollama.
    """
    return detect_research_gap(title, abstract)
def generate_literature_review_service(title: str, abstract: str):
    """
    Generate a literature review using Ollama.
    """
    return generate_literature_review(title, abstract)
def analyze_research_trends_service(title: str, abstract: str):
    """
    Generate AI-powered research trend analysis.
    """

    return analyze_research_trends(title, abstract)
def citation_intelligence(
    title,
    authors,
    journal,
    publication_year,
    doi
):
    return generate_citations(
        title,
        authors,
        journal,
        publication_year,
        doi
    )
def research_chat_assistant(
    title,
    abstract,
    question
):
    return research_chat(
        title,
        abstract,
        question
    )
def paper_comparator(
    title1,
    abstract1,
    title2,
    abstract2
):
    return compare_research_papers(
        title1,
        abstract1,
        title2,
        abstract2
    )
def research_proposal_generator(title, abstract):
    return generate_research_proposal(
        title,
        abstract
    )
def novelty_checker(
    title,
    abstract
):
    return check_novelty(
        title,
        abstract
    )
def research_question_generator(
    title,
    abstract
):
    return generate_research_questions(
        title,
        abstract

    )
def methodology_recommender(title, abstract):
    return recommend_methodology(title, abstract)