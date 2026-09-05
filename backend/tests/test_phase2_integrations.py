def _create_profile(client, headers, domains="AI, Robotics"):
    return client.post(
        "/api/v1/profile/",
        json={"research_domains": domains, "organization_name": "Test University"},
        headers=headers,
    )


def test_orcid_search_requires_auth(client):
    response = client.get("/api/v1/profile/orcid/search", params={"name": "Jane Doe"})
    assert response.status_code == 401


def test_orcid_works_requires_auth(client):
    response = client.get(
        "/api/v1/profile/orcid/works", params={"orcid_id": "0000-0002-1825-0097"}
    )
    assert response.status_code == 401


def test_crossref_search_requires_auth(client):
    response = client.get("/api/v1/profile/crossref/search", params={"query": "graphene"})
    assert response.status_code == 401


def test_profile_can_save_orcid_id(client, registered_user):
    response = _create_profile(client, registered_user)
    assert response.status_code == 200

    updated = client.post(
        "/api/v1/profile/",
        json={
            "research_domains": "AI, Robotics",
            "organization_name": "Test University",
            "orcid_id": "0000-0002-1825-0097",
        },
        headers=registered_user,
    )
    assert updated.status_code == 200
    assert updated.json()["orcid_id"] == "0000-0002-1825-0097"


def test_funding_explanation_matches_overlapping_domain(client, registered_user, admin_user):
    _create_profile(client, registered_user, domains="Robotics, Biotech")

    funding_response = client.post(
        "/api/v1/funding/",
        json={
            "title": "Robotics Innovation Grant",
            "domains": "Robotics, Automation",
            "eligibility": "all",
        },
        headers=admin_user,
    )
    assert funding_response.status_code == 200
    funding_id = funding_response.json()["id"]

    explanation = client.get(
        f"/api/v1/profile/funding/{funding_id}/explanation", headers=registered_user
    )
    assert explanation.status_code == 200
    body = explanation.json()
    assert body["is_recommended"] is True
    assert len(body["matched_keywords"]) > 0
    assert len(body["reasons"]) > 0


def test_funding_explanation_no_match_for_unrelated_domain(client, registered_user, admin_user):
    _create_profile(client, registered_user, domains="Marine Biology")

    funding_response = client.post(
        "/api/v1/funding/",
        json={
            "title": "Quantum Computing Grant",
            "domains": "Quantum Computing",
            "eligibility": "all",
        },
        headers=admin_user,
    )
    funding_id = funding_response.json()["id"]

    explanation = client.get(
        f"/api/v1/profile/funding/{funding_id}/explanation", headers=registered_user
    )
    assert explanation.status_code == 200
    body = explanation.json()
    assert body["is_recommended"] is False
    assert body["matched_keywords"] == []


def test_funding_explanation_requires_profile(client, registered_user, admin_user):
    funding_response = client.post(
        "/api/v1/funding/",
        json={"title": "Some Grant", "domains": "AI", "eligibility": "all"},
        headers=admin_user,
    )
    funding_id = funding_response.json()["id"]

    explanation = client.get(
        f"/api/v1/profile/funding/{funding_id}/explanation", headers=registered_user
    )
    assert explanation.status_code == 404