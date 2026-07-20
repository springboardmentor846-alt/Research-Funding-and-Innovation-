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