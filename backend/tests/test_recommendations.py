def test_recommendations_require_auth(client):
    response = client.get("/api/v1/recommendations/funding")
    assert response.status_code == 401


def test_recommendations_require_profile_first(client, registered_user):
    response = client.get("/api/v1/recommendations/funding", headers=registered_user)
    assert response.status_code == 404


def test_recommended_funding_ranks_by_similarity(client, registered_user, admin_user):
    client.post(
        "/api/v1/profile/",
        json={
            "research_domains": "Artificial Intelligence, Machine Learning",
            "keywords": "neural networks, deep learning",
        },
        headers=registered_user,
    )

    client.post(
        "/api/v1/funding/",
        json={
            "title": "AI Research Grant",
            "description": "Funding for artificial intelligence and machine learning research",
            "domains": "Artificial Intelligence",
        },
        headers=admin_user,
    )
    client.post(
        "/api/v1/funding/",
        json={
            "title": "Marine Biology Grant",
            "description": "Funding for ocean and coral reef conservation studies",
            "domains": "Marine Biology",
        },
        headers=admin_user,
    )

    response = client.get("/api/v1/recommendations/funding", headers=registered_user)
    assert response.status_code == 200
    results = response.json()
    assert len(results) >= 1
    assert results[0]["title"] == "AI Research Grant"


def test_recommended_collaborators(client):
    for email, domain in [
        ("researcher_a@example.com", "Artificial Intelligence"),
        ("researcher_b@example.com", "Artificial Intelligence"),
        ("researcher_c@example.com", "Marine Biology"),
    ]:
        client.post(
            "/api/v1/auth/register",
            json={"name": email, "email": email, "password": "testpass123", "role": "researcher"},
        )
        login = client.post("/api/v1/auth/login", json={"email": email, "password": "testpass123"})
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
        client.post("/api/v1/profile/", json={"research_domains": domain}, headers=headers)

    login_a = client.post(
        "/api/v1/auth/login", json={"email": "researcher_a@example.com", "password": "testpass123"}
    )
    headers_a = {"Authorization": f"Bearer {login_a.json()['access_token']}"}

    response = client.get("/api/v1/recommendations/collaborators", headers=headers_a)
    assert response.status_code == 200
    results = response.json()
    assert len(results) >= 1
    assert results[0]["name"] == "researcher_b@example.com"