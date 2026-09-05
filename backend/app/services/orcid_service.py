"""
ORCID integration.

Uses ORCID's public API (pub.orcid.org) which requires no API key or
registration — it's free and open for reading public researcher records.
Docs: https://info.orcid.org/documentation/features/public-api/
"""
import requests
from app.core.cache import ttl_cache

BASE_URL = "https://pub.orcid.org/v3.0"
HEADERS = {"Accept": "application/json"}


@ttl_cache(seconds=300)
def search_orcid_by_name(name: str, limit: int = 5):
    """
    Searches the public ORCID registry for researchers matching a name.
    Returns a list of {orcid_id, name} candidates the user can pick from.
    """
    url = f"{BASE_URL}/expanded-search/"
    query = f'given-and-family-names:"{name}"'

    try:
        response = requests.get(
            url,
            params={"q": query, "rows": limit},
            headers=HEADERS,
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        return []

    results = []
    for item in data.get("expanded-result", []) or []:
        orcid_id = item.get("orcid-id")
        if not orcid_id:
            continue
        given = item.get("given-names") or ""
        family = item.get("family-names") or ""
        display_name = (item.get("credit-name") or f"{given} {family}").strip()
        results.append({
            "orcid_id": orcid_id,
            "name": display_name or "Unknown",
        })
    return results


def get_orcid_works(orcid_id: str):
    """
    Fetches the list of works (publications) recorded on a researcher's
    public ORCID profile, given their ORCID iD (e.g. "0000-0002-1825-0097").
    """
    orcid_id = orcid_id.strip()
    url = f"{BASE_URL}/{orcid_id}/works"

    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()
    data = response.json()

    publications = []
    for group in data.get("group", []) or []:
        summaries = group.get("work-summary", [])
        if not summaries:
            continue
        summary = summaries[0]  # first summary in the group is representative

        title_block = (summary.get("title") or {}).get("title") or {}
        title = (title_block.get("value") or "").strip()
        if not title:
            continue

        pub_date = summary.get("publication-date") or {}
        year_block = pub_date.get("year") or {}
        year = year_block.get("value")

        journal_block = summary.get("journal-title") or {}
        source = journal_block.get("value") or "ORCID record"

        link = None
        external_ids = (summary.get("external-ids") or {}).get("external-id") or []
        for ext_id in external_ids:
            if ext_id.get("external-id-type") == "doi":
                doi_value = ext_id.get("external-id-value")
                if doi_value:
                    link = f"https://doi.org/{doi_value}"
                    break
        if not link:
            link = f"https://orcid.org/{orcid_id}"

        publications.append({
            "title": title[:500],
            "authors": None,  # ORCID work summaries don't include a full author list
            "year": str(year) if year else None,
            "source": source[:255],
            "link": link,
        })

    return publications