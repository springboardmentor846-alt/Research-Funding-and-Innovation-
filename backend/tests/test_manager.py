def test_manager_routes_require_auth(client):
    response = client.get("/api/v1/manager/overview")
    assert response.status_code == 401


def test_manager_routes_forbidden_for_researcher(client, registered_user):
    response = client.get("/api/v1/manager/overview", headers=registered_user)
    assert response.status_code == 403


def test_manager_overview_allowed_for_admin(client, admin_user):
    response = client.get("/api/v1/manager/overview", headers=admin_user)
    assert response.status_code == 200
    assert "total_users" in response.json()


def test_manager_overview_allowed_for_innovation_manager(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Manager One",
            "email": "manager1@example.com",
            "password": "managerpass123",
            "role": "innovation_manager",
        },
    )
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "manager1@example.com", "password": "managerpass123"},
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = client.get("/api/v1/manager/overview", headers=headers)
    assert response.status_code == 200

    startups_response = client.get("/api/v1/manager/startups", headers=headers)
    assert startups_response.status_code == 200
    assert startups_response.json() == []

    activity_response = client.get("/api/v1/manager/collaboration-activity", headers=headers)
    assert activity_response.status_code == 200
    assert activity_response.json() == []