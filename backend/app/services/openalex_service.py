import requests

BASE_URL = "https://api.openalex.org"


def search_author(author_name: str):
    """
    Search authors by name.
    """

    url = f"{BASE_URL}/authors"

    response = requests.get(
        url,
        params={
            "search": author_name,
            "per-page": 5
        },
        timeout=20
    )

    response.raise_for_status()

    return response.json()


def get_author_works(author_id: str):
    """
    Fetch publications of an OpenAlex author.
    """

    author_id = author_id.split("/")[-1]

    url = f"{BASE_URL}/works"

    response = requests.get(
        url,
        params={
            "filter": f"author.id:https://openalex.org/{author_id}",
            "per-page": 25
        },
        timeout=20
    )

    response.raise_for_status()

    return response.json()


def extract_publications(author_id: str):

    works = get_author_works(author_id)

    publications = []

    for work in works.get("results", []):

        # DOI
        doi = work.get("doi")

        if doi:
            doi = doi.replace(
                "https://doi.org/",
                ""
            )

        # Source
        primary_location = work.get("primary_location") or {}

        source_info = primary_location.get("source") or {}

        # Safe string lengths
        title = (
            work.get("display_name") or ""
        )[:500]

        journal_name = (
            source_info.get("display_name") or ""
        )[:500]

        publisher = (
            source_info.get("host_organization_name")
            or source_info.get("display_name")
            or ""
        )[:255]

        # Authors
        authors = []

        for author in work.get("authorships", []):

            author_info = author.get("author") or {}

            authors.append(
                author_info.get(
                    "display_name",
                    ""
                )
            )

        # Text column can store long strings,
        # but we'll keep it reasonable.
        authors_text = ", ".join(authors)[:5000]

        # Publication Date
        publication_date = None

        publication_date_str = work.get(
            "publication_date"
        )

        if publication_date_str:
            try:
                from datetime import date

                publication_date = date.fromisoformat(
                    publication_date_str
                )

            except Exception:
                publication_date = None

        # Research Domain
        research_domain = None

        concepts = work.get("concepts") or []

        if concepts:
            research_domain = (
                concepts[0].get("display_name") or ""
            )[:255]

        publications.append(
            {
                "title": title,

                "publication_type": work.get("type"),

                "authors": authors_text,

                "journal_or_conference": journal_name,

                "publisher": publisher,

                "publication_date": publication_date,

                "doi": doi,

                "url": work.get("id"),

                "abstract": None,

                "openalex_id": work.get("id"),

                "citation_count": work.get(
                    "cited_by_count",
                    0
                ),

                "research_domain": research_domain,

                "language": work.get("language"),

                "source": "OpenAlex",

                "is_open_access": (
                    work.get("open_access") or {}
                ).get(
                    "is_oa",
                    False
                )
            }
        )

    return publications