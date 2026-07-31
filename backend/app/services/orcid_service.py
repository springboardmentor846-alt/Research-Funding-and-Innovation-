from datetime import date

import requests


BASE_URL = "https://pub.orcid.org/v3.0"


def get_orcid_profile(orcid_id: str):

    headers = {
        "Accept": "application/json"
    }

    response = requests.get(
        f"{BASE_URL}/{orcid_id}/person",
        headers=headers,
        timeout=20
    )

    response.raise_for_status()

    return response.json()


def get_orcid_works(orcid_id: str):

    headers = {
        "Accept": "application/json"
    }

    response = requests.get(
        f"{BASE_URL}/{orcid_id}/works",
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def extract_orcid_publications(orcid_data):

    publications = []

    groups = orcid_data.get("group", [])

    for group in groups:

        summaries = group.get(
            "work-summary",
            []
        )

        if not summaries:
            continue

        work = summaries[0]

        title_data = (
            work.get("title") or {}
        ).get("title") or {}

        title = title_data.get("value")

        if not title:
            continue

        publication_type = work.get("type")

        journal = (
            work.get("journal-title") or {}
        ).get("value")

        publication_date_data = (
            work.get("publication-date") or {}
        )

        year = (
            publication_date_data.get("year") or {}
        ).get("value")

        month = (
            publication_date_data.get("month") or {}
        ).get("value")

        day = (
            publication_date_data.get("day") or {}
        ).get("value")

        parsed_date = None

        if year:
            try:
                parsed_date = date(
                    int(year),
                    int(month) if month else 1,
                    int(day) if day else 1
                )
            except ValueError:
                parsed_date = None

        doi = None
        url = None

        external_ids = (
            work.get("external-ids") or {}
        ).get(
            "external-id",
            []
        )

        for external_id in external_ids:

            id_type = (
                external_id.get(
                    "external-id-type"
                ) or ""
            ).lower()

            id_value = external_id.get(
                "external-id-value"
            )

            if id_type == "doi" and id_value:
                doi = id_value

            external_url = (
                external_id.get(
                    "external-id-url"
                ) or {}
            ).get("value")

            if external_url and not url:
                url = external_url

        publications.append({
            "title": title,
            "publication_type": publication_type,
            "journal_or_conference": journal,
            "publication_date": parsed_date,
            "doi": doi,
            "url": url,
            "source": "ORCID"
        })

    return publications