def _create_profile(client, headers, domains="AI, Robotics", keywords="machine learning, deep learning"):
    return client.post(
        "/api/v1/profile/",
        json={
            "research_domains": domains,
            "keywords": keywords,
            "technology_areas": "Neural Networks",
            "organization_name": "Test University",
        },
        headers=headers,
    )


def test_predict_success_requires_profile(client, registered_user, admin_user):
    funding_response = client.post(
        "/api/v1/funding/",
        json={"title": "AI Grant", "domains": "AI", "eligibility": "all"},
        headers=admin_user,
    )
    funding_id = funding_response.json()["id"]

    response = client.get(
        f"/api/v1/profile/funding/{funding_id}/predict-success", headers=registered_user
    )
    assert response.status_code == 404


def test_predict_success_returns_probability_and_features(client, registered_user, admin_user):
    _create_profile(client, registered_user)

    client.post(
        "/api/v1/profile/publications",
        json={"title": "A study on machine learning for robotics", "year": "2024"},
        headers=registered_user,
    )

    funding_response = client.post(
        "/api/v1/funding/",
        json={
            "title": "AI Research Grant",
            "domains": "Artificial Intelligence, Robotics",
            "description": "Funding for machine learning and robotics research.",
            "eligibility": "all",
        },
        headers=admin_user,
    )
    funding_id = funding_response.json()["id"]

    response = client.get(
        f"/api/v1/profile/funding/{funding_id}/predict-success", headers=registered_user
    )
    assert response.status_code == 200
    body = response.json()

    assert "success_probability" in body
    assert 0 <= body["success_probability"] <= 100
    assert body["rating"] in ("Strong Match", "Moderate Match", "Low Match")
    assert "features" in body
    assert body["features"]["publications_count"] == 1
    assert body["features"]["domains_count"] == 2


def test_predict_success_requires_auth(client):
    response = client.get("/api/v1/profile/funding/1/predict-success")
    assert response.status_code == 401


def test_predict_success_unknown_funding_returns_404(client, registered_user):
    _create_profile(client, registered_user)
    response = client.get(
        "/api/v1/profile/funding/999999/predict-success", headers=registered_user
    )
    assert response.status_code == 404