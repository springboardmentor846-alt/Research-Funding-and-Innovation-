"""
Lens.org Patent API client.

Requires a LENS_API_KEY. Lens.org offers free/academic API access —
register at https://www.lens.org (Scholarly & Patent API access request).
The key is checked lazily (only when a search is actually made), so a
missing key never crashes the whole application at startup — it only
surfaces as a clear error the moment someone tries to use this feature.
"""
import os

import requests
from dotenv import load_dotenv

load_dotenv()

LENS_API_KEY = os.getenv("LENS_API_KEY")
BASE_URL = "https://api.lens.org/patent/search"


class LensNotConfiguredError(Exception):
    """Raised when a Lens search is attempted but no LENS_API_KEY is set."""


def search_patents(query: str, size: int = 25):
    if not LENS_API_KEY:
        raise LensNotConfiguredError(
            "LENS_API_KEY is not configured. Request free API access at "
            "https://www.lens.org and add it to your .env file."
        )

    headers = {
        "Authorization": f"Bearer {LENS_API_KEY}",
        "Content-Type": "application/json",
    }

    body = {
        "query": {
            "match": {
                "title": query
            }
        },
        "size": size,
    }

    response = requests.post(BASE_URL, headers=headers, json=body, timeout=30)
    response.raise_for_status()

    return response.json()