import requests

from app.config import settings

BASE_URL = "https://api.lens.org/patent/search"


def search_patents(query: str, size: int = 25):

    headers = {
        "Authorization": f"Bearer {settings.LENS_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "query": {
            "match": {
                "title": query
            }
        },
        "size": size
    }

    response = requests.post(
        BASE_URL,
        headers=headers,
        json=body,
        timeout=30
    )

    response.raise_for_status()

    return response.json()