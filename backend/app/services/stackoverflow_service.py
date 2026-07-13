import httpx


class StackOverflowService:

    BASE_URL = "https://api.stackexchange.com/2.3/search"

    async def search(self, keyword: str):

        params = {
            "order": "desc",
            "sort": "votes",
            "intitle": keyword,
            "site": "stackoverflow",
            "pagesize": 10
        }

        async with httpx.AsyncClient(timeout=60) as client:

            response = await client.get(
                self.BASE_URL,
                params=params
            )

        if response.status_code != 200:
            return None

        data = response.json()

        return data.get("items", [])