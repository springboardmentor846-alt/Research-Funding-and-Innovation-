import os
import httpx

BASE_URL = "https://api.openalex.org"
HEADERS = {
    "User-Agent": "ResearchFundingPlatform/1.0 (mailto:lingeswarreddy090@gmail.com)"
}

class OpenAlexService:

    async def search(self, keyword: str):

        async with httpx.AsyncClient(timeout=60, headers=HEADERS) as client:

            response = await client.get(
                f"{BASE_URL}/works",
                params={
                    "search": keyword,
                    "per-page": 10
                }
            )

        if response.status_code == 429:
            return {
                "success": False,
                "message": "OpenAlex rate limit exceeded. Please wait 1 minute and try again."}
        response.raise_for_status()

        return response.json()