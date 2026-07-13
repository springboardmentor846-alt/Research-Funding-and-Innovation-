import os
import httpx


class GitHubService:

    BASE_URL = "https://api.github.com/search/repositories"

    async def search(self, keyword: str):

        params = {
            "q": keyword,
            "sort": "stars",
            "order": "desc",
            "per_page": 1
        }

        headers = {
            "User-Agent": "ResearchFundingPlatform"
        }

        # Optional GitHub Token
        github_token = os.getenv("GITHUB_TOKEN")

        if github_token:
            headers["Authorization"] = f"Bearer {github_token}"

        try:

            async with httpx.AsyncClient(
                timeout=httpx.Timeout(60.0)
            ) as client:

                response = await client.get(
                    self.BASE_URL,
                    params=params,
                    headers=headers
                )

            if response.status_code != 200:

                print("GitHub API Error:", response.status_code)
                print(response.text)

                return None

            data = response.json()

            if data.get("total_count", 0) == 0:
                return None

            repo = data["items"][0]

            # Debug Output
            print("\n========== GitHub Repository ==========")
            print("Repository :", repo.get("full_name"))
            print("Stars      :", repo.get("stargazers_count"))
            print("Forks      :", repo.get("forks_count"))
            print("Watchers   :", repo.get("watchers_count"))
            print("=======================================\n")

            return {

                "name": repo.get("full_name"),

                "stars": repo.get("stargazers_count", 0),

                "forks": repo.get("forks_count", 0),

                "watchers": repo.get("watchers_count", 0)

            }

        except httpx.ConnectTimeout:

            print("GitHub Connection Timeout")

            return None

        except Exception as e:

            print("GitHub Error:", str(e))

            return None