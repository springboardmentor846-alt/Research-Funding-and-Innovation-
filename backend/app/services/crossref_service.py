import requests

BASE_URL = "https://api.crossref.org/works"


def get_publication_metadata(doi: str):

    response = requests.get(
        f"{BASE_URL}/{doi}",
        timeout=20
    )

    response.raise_for_status()

    return response.json()["message"]