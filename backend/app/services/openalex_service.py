from datetime import date

import requests


BASE_URL = "https://api.openalex.org"


# ============================================================
# SEARCH PUBLICATIONS
# ============================================================

def search_openalex_publications(
    query: str,
    per_page: int = 10
):

    query = query.strip()

    if not query:
        return []

    per_page = min(
        max(per_page, 1),
        50
    )

    response = requests.get(
        f"{BASE_URL}/works",
        params={
            "search": query,
            "per-page": per_page,
        },
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    return data.get("results", [])


# ============================================================
# ABSTRACT
# ============================================================

def reconstruct_abstract(
    inverted_index
):

    if not inverted_index:
        return None

    words = []

    for word, positions in inverted_index.items():

        for position in positions:
            words.append(
                (position, word)
            )

    words.sort(
        key=lambda item: item[0]
    )

    abstract = " ".join(
        word
        for _, word in words
    )

    return abstract


# ============================================================
# CONVERT OPENALEX WORK
# ============================================================

def parse_openalex_work(work):

    openalex_id = work.get("id")

    if not openalex_id:
        return None

    title = (
        work.get("display_name")
        or work.get("title")
        or "Untitled publication"
    )[:500]

    # --------------------------------------------------------
    # DOI
    # --------------------------------------------------------

    doi = work.get("doi")

    if doi:
        doi = doi.replace(
            "https://doi.org/",
            ""
        )

    # --------------------------------------------------------
    # AUTHORS
    # --------------------------------------------------------

    author_names = []

    for authorship in work.get(
        "authorships",
        []
    ):

        author = (
            authorship.get("author")
            or {}
        )

        name = author.get(
            "display_name"
        )

        if name:
            author_names.append(name)

    authors = ", ".join(
        author_names
    )

    # --------------------------------------------------------
    # SOURCE
    # --------------------------------------------------------

    primary_location = (
        work.get("primary_location")
        or {}
    )

    source_data = (
        primary_location.get("source")
        or {}
    )

    journal = source_data.get(
        "display_name"
    )

    publisher = (
        source_data.get(
            "host_organization_name"
        )
        or source_data.get(
            "display_name"
        )
    )

    # --------------------------------------------------------
    # DATE
    # --------------------------------------------------------

    publication_date = None

    publication_date_raw = work.get(
        "publication_date"
    )

    if publication_date_raw:

        try:

            publication_date = (
                date.fromisoformat(
                    publication_date_raw
                )
            )

        except ValueError:
            publication_date = None

    # --------------------------------------------------------
    # RESEARCH DOMAIN
    # --------------------------------------------------------

    research_domain = None

    topics = work.get(
        "topics"
    ) or []

    if topics:

        primary_topic = topics[0]

        domain = (
            primary_topic.get("domain")
            or {}
        )

        field = (
            primary_topic.get("field")
            or {}
        )

        research_domain = (
            field.get("display_name")
            or domain.get("display_name")
        )

    # --------------------------------------------------------
    # ABSTRACT
    # --------------------------------------------------------

    abstract = reconstruct_abstract(
        work.get(
            "abstract_inverted_index"
        )
    )

    # --------------------------------------------------------
    # OPEN ACCESS
    # --------------------------------------------------------

    open_access = (
        work.get("open_access")
        or {}
    )

    is_open_access = bool(
        open_access.get(
            "is_oa",
            False
        )
    )

    # --------------------------------------------------------
    # URL
    # --------------------------------------------------------

    publication_url = None

    best_oa_location = (
        work.get(
            "best_oa_location"
        )
        or {}
    )

    publication_url = (
        best_oa_location.get(
            "landing_page_url"
        )
        or primary_location.get(
            "landing_page_url"
        )
        or openalex_id
    )

    return {

        "research_profile_id": None,

        "title": title,

        "publication_type": (
            work.get("type")
        ),

        "authors": authors or None,

        "journal_or_conference": (
            journal[:500]
            if journal
            else None
        ),

        "publisher": (
            publisher[:255]
            if publisher
            else None
        ),

        "publication_date": (
            publication_date
        ),

        "doi": doi,

        "url": publication_url,

        "abstract": abstract,

        "openalex_id": openalex_id,

        "citation_count": (
            work.get(
                "cited_by_count",
                0
            )
            or 0
        ),

        "research_domain": (
            research_domain[:255]
            if research_domain
            else None
        ),

        "language": (
            work.get("language")
        ),

        "source": "OpenAlex",

        "is_open_access": (
            is_open_access
        ),
    }


# ============================================================
# SEARCH + PARSE
# ============================================================

def get_publications_by_topic(
    query: str,
    limit: int = 10
):

    works = search_openalex_publications(
        query=query,
        per_page=limit
    )

    publications = []

    for work in works:

        publication = (
            parse_openalex_work(work)
        )

        if publication:
            publications.append(
                publication
            )

    return publications