import asyncio

from app.patents.providers.lens_client import LensClientConfig, LensPatentClient


class DummyResponse:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = payload or {"data": [], "total": 0}
        self.headers = {}
        self.text = "{}"

    def json(self):
        return self._payload


class DummyAsyncClient:
    def __init__(self, *args, **kwargs):
        self.calls = []

    async def post(self, path, json=None):
        self.calls.append((path, json))
        return DummyResponse(status_code=200, payload={"data": [], "total": 0})

    async def aclose(self):
        return None


def test_search_uses_documented_patent_endpoint(monkeypatch):
    dummy_client = DummyAsyncClient()

    def build_client(*args, **kwargs):
        return dummy_client

    monkeypatch.setattr("app.patents.providers.lens_client.httpx.AsyncClient", build_client)

    async def run_test():
        client = LensPatentClient(
            LensClientConfig(base_url="https://api.lens.org", token="test-token")
        )
        await client.search(query="*", from_offset=0, size=1)
        await client.aclose()
        assert dummy_client.calls[0][0] == "/patent/search"

    asyncio.run(run_test())
