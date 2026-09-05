def test_list_funding_sources(client):
    response = client.get("/api/v1/funding/sources")
    assert response.status_code == 200
    sources = response.json()["sources"]
    for expected in ["horizon", "ukri", "anrf", "birac", "dbt", "icmr", "wellcome"]:
        assert expected in sources


def test_search_live_source_requires_auth(client):
    response = client.get(
        "/api/v1/funding/search-live-sources/anrf", params={"keyword": "research"}
    )
    assert response.status_code == 401


def test_search_live_source_unknown_source_returns_404(client, registered_user):
    response = client.get(
        "/api/v1/funding/search-live-sources/not-a-real-source",
        params={"keyword": "research"},
        headers=registered_user,
    )
    assert response.status_code == 404


def test_search_anrf_returns_curated_results(client, registered_user):
    response = client.get(
        "/api/v1/funding/search-live-sources/anrf",
        params={"keyword": ""},
        headers=registered_user,
    )
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
    assert results[0]["source"] == "ANRF (India)"


def test_search_birac_returns_results_live_or_fallback(client, registered_user):
    """BIRAC is live-scraped; if the site is unreachable/changed, a curated fallback kicks in — either way this must never be empty or crash."""
    response = client.get(
        "/api/v1/funding/search-live-sources/birac",
        params={"keyword": "biotech"},
        headers=registered_user,
    )
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
    assert all("source" in r and "title" in r and "link" in r for r in results)


def test_search_dbt_returns_results_live_or_fallback(client, registered_user):
    response = client.get(
        "/api/v1/funding/search-live-sources/dbt",
        params={"keyword": ""},
        headers=registered_user,
    )
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_search_icmr_returns_results_live_or_fallback(client, registered_user):
    response = client.get(
        "/api/v1/funding/search-live-sources/icmr",
        params={"keyword": ""},
        headers=registered_user,
    )
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_search_wellcome_returns_curated_results(client, registered_user):
    response = client.get(
        "/api/v1/funding/search-live-sources/wellcome",
        params={"keyword": ""},
        headers=registered_user,
    )
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_search_horizon_never_crashes_even_if_api_unreachable(client, registered_user):
    """
    Horizon hits a real external API. In a sandboxed/offline test run it
    may return an empty list, but the endpoint itself must never error out.
    """
    response = client.get(
        "/api/v1/funding/search-live-sources/horizon",
        params={"keyword": "climate"},
        headers=registered_user,
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_search_ukri_never_crashes_even_if_api_unreachable(client, registered_user):
    response = client.get(
        "/api/v1/funding/search-live-sources/ukri",
        params={"keyword": "climate"},
        headers=registered_user,
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)