import os
import httpx

BASE_URL = "https://api.semanticscholar.org/graph/v1"


class SemanticScholarService:

    async def search(self, keyword: str):

        async with httpx.AsyncClient(
            timeout=60,
        ) as client:

            response = await client.get(
                f"{BASE_URL}/paper/search",
                params={
                    "query": keyword,
                    "limit": 3,
                    "fields": "title,authors,year,citationCount,influentialCitationCount,venue,fieldsOfStudy"
                }
            )

        if response.status_code == 429:
            return {
                "success": False,
                "source": "Semantic Scholar",
                "message": "Rate limit exceeded. Using OpenAlex data instead."}

        response.raise_for_status()

        return response.json()