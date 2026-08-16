import requests
from app.core.cache import ttl_cache

BASE_URL = "https://api.openalex.org"


@ttl_cache(seconds=300)
def search_author(author_name: str):
    url = f"{BASE_URL}/authors"
    response = requests.get(
        url,
        params={"search": author_name, "per-page": 5},
        timeout=20,
    )
    response.raise_for_status()
    data = response.json()

    authors = []
    for author in data.get("results", []):
        authors.append(
            {
                "id": author.get("id"),
                "name": author.get("display_name"),
                "works_count": author.get("works_count"),
                "cited_by_count": author.get("cited_by_count"),
            }
        )
    return authors


def get_author_works(author_id: str):
    author_id = author_id.split("/")[-1]
    url = f"{BASE_URL}/works"
    response = requests.get(
        url,
        params={
            "filter": f"author.id:https://openalex.org/{author_id}",
            "per-page": 25,
        },
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def extract_publications(author_id: str):
    works = get_author_works(author_id)
    publications = []

    for work in works.get("results", []):
        title = (work.get("display_name") or "")[:500]

        authors_list = []
        for authorship in work.get("authorships", []):
            author_info = authorship.get("author") or {}
            name = author_info.get("display_name")
            if name:
                authors_list.append(name)
        authors_text = ", ".join(authors_list)[:1000]

        year = work.get("publication_year")
        year_str = str(year) if year else None

        primary_location = work.get("primary_location") or {}
        source_info = primary_location.get("source") or {}
        source_name = (source_info.get("display_name") or "OpenAlex")[:255]

        link = work.get("id")

        publications.append(
            {
                "title": title,
                "authors": authors_text,
                "year": year_str,
                "source": source_name,
                "link": link,
            }
        )

    return publications