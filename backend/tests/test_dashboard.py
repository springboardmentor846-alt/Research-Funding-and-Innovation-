def test_dashboard_requires_auth(client):
    response = client.get("/api/v1/dashboard/overview")
    assert response.status_code == 401


def test_my_dashboard_overview(client, registered_user):
    response = client.get("/api/v1/dashboard/overview", headers=registered_user)
    assert response.status_code == 200
    body = response.json()
    assert body["has_research_profile"] is False
    assert body["publication_count"] == 0
    assert "collaboration_requests" in body


def test_platform_dashboard_forbidden_for_researcher(client, registered_user):
    response = client.get("/api/v1/dashboard/platform", headers=registered_user)
    assert response.status_code == 403


def test_platform_dashboard_allowed_for_admin(client, admin_user):
    response = client.get("/api/v1/dashboard/platform", headers=admin_user)
    assert response.status_code == 200
    body = response.json()
    assert "total_users" in body
    assert "users_by_role" in body