def _register_and_login(client, email, role="startup_founder"):
    client.post(
        "/api/v1/auth/register",
        json={"name": email.split("@")[0], "email": email, "password": "password123", "role": role},
    )
    login = client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_startup_profile_requires_startup_role(client, registered_user):
    """registered_user fixture is a 'researcher' — startup endpoints should reject it."""
    response = client.post(
        "/api/v1/startup/profile",
        json={"startup_name": "TestCo"},
        headers=registered_user,
    )
    assert response.status_code == 403


def test_create_and_get_startup_profile(client):
    headers = _register_and_login(client, "founder1@example.com")

    create_response = client.post(
        "/api/v1/startup/profile",
        json={
            "startup_name": "GreenTech Solutions",
            "industry": "Clean Energy",
            "stage": "Seed",
            "technology_stack": "IoT, Machine Learning",
        },
        headers=headers,
    )
    assert create_response.status_code == 200
    assert create_response.json()["startup_name"] == "GreenTech Solutions"

    get_response = client.get("/api/v1/startup/profile", headers=headers)
    assert get_response.status_code == 200
    assert get_response.json()["industry"] == "Clean Energy"


def test_cannot_create_duplicate_startup_profile(client):
    headers = _register_and_login(client, "founder2@example.com")

    client.post(
        "/api/v1/startup/profile",
        json={"startup_name": "First Try"},
        headers=headers,
    )
    second = client.post(
        "/api/v1/startup/profile",
        json={"startup_name": "Second Try"},
        headers=headers,
    )
    assert second.status_code == 400


def test_update_startup_profile(client):
    headers = _register_and_login(client, "founder3@example.com")

    client.post(
        "/api/v1/startup/profile",
        json={"startup_name": "Original Name", "stage": "Idea"},
        headers=headers,
    )
    update_response = client.put(
        "/api/v1/startup/profile",
        json={"startup_name": "Updated Name", "stage": "Series A"},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["startup_name"] == "Updated Name"
    assert update_response.json()["stage"] == "Series A"


def test_find_researchers_as_startup(client):
    headers = _register_and_login(client, "founder4@example.com")

    researcher_headers = _register_and_login(client, "researcher4@example.com", role="researcher")
    client.post(
        "/api/v1/profile/",
        json={"research_domains": "AI, Robotics", "organization_name": "Test University"},
        headers=researcher_headers,
    )

    response = client.get("/api/v1/startup/researchers", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["count"] >= 1
    assert any(r["organization_name"] == "Test University" for r in body["researchers"])


def test_find_startups_excludes_self(client):
    headers = _register_and_login(client, "founder5@example.com")
    client.post(
        "/api/v1/startup/profile",
        json={"startup_name": "Founder Five Co"},
        headers=headers,
    )

    other_headers = _register_and_login(client, "founder6@example.com")
    client.post(
        "/api/v1/startup/profile",
        json={"startup_name": "Founder Six Co"},
        headers=other_headers,
    )

    response = client.get("/api/v1/startup/startups", headers=headers)
    assert response.status_code == 200
    names = [s["startup_name"] for s in response.json()["startups"]]
    assert "Founder Six Co" in names
    assert "Founder Five Co" not in names


def test_startup_predict_success_requires_profile(client, admin_user):
    headers = _register_and_login(client, "founder7@example.com")

    funding_response = client.post(
        "/api/v1/funding/",
        json={"title": "Clean Energy Grant", "domains": "Clean Energy", "eligibility": "all"},
        headers=admin_user,
    )
    funding_id = funding_response.json()["id"]

    response = client.get(f"/api/v1/startup/predict-success/{funding_id}", headers=headers)
    assert response.status_code == 404


def test_startup_predict_success_returns_scores(client, admin_user):
    headers = _register_and_login(client, "founder8@example.com")
    client.post(
        "/api/v1/startup/profile",
        json={
            "startup_name": "AgriTech Co",
            "industry": "Agriculture Technology",
            "stage": "Seed",
            "technology_stack": "IoT sensors, machine learning for crop monitoring",
            "problem_statement": "Farmers lack real-time crop health data",
            "solution": "IoT-based crop monitoring platform",
            "team_size": 3,
        },
        headers=headers,
    )

    funding_response = client.post(
        "/api/v1/funding/",
        json={
            "title": "AgriTech Innovation Grant",
            "domains": "Agriculture Technology, IoT",
            "description": "Funding for IoT and machine learning solutions in agriculture.",
            "eligibility": "all",
        },
        headers=admin_user,
    )
    funding_id = funding_response.json()["id"]

    response = client.get(f"/api/v1/startup/predict-success/{funding_id}", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert "success_estimate" in body
    assert "match_score" in body
    assert "readiness_score" in body
    assert "strengths" in body
    assert "improvements" in body