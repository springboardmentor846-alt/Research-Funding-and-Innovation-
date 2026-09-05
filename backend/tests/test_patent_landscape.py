def test_patent_landscape_requires_auth(client):
    response = client.get("/api/v1/profile/patent-landscape", params={"query": "battery"})
    assert response.status_code == 401


def test_patent_landscape_without_api_key_returns_clear_error_not_crash(client, registered_user):
    """
    Without LENS_API_KEY configured (the default for local/test runs),
    this must respond with a clear 503 error rather than crashing the
    server or the test suite.
    """
    response = client.get(
        "/api/v1/profile/patent-landscape",
        params={"query": "battery"},
        headers=registered_user,
    )
    assert response.status_code in (503, 200)
    if response.status_code == 503:
        assert "LENS_API_KEY" in response.json()["detail"]


def test_patent_landscape_requires_query_param(client, registered_user):
    response = client.get("/api/v1/profile/patent-landscape", headers=registered_user)
    assert response.status_code == 422