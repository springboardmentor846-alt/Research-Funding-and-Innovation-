def test_create_profile_requires_authentication(client):
    response = client.post("/api/v1/profile/", json={"research_domains": "AI"})
    assert response.status_code == 401


def test_create_and_get_profile(client, registered_user):
    response = client.post(
        "/api/v1/profile/",
        json={
            "research_domains": "AI, Blockchain",
            "keywords": "machine learning",
            "technology_areas": "Software",
            "organization_name": "Test University",
        },
        headers=registered_user,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["research_domains"] == "AI, Blockchain"
    assert body["organization_name"] == "Test University"

    get_response = client.get("/api/v1/profile/", headers=registered_user)
    assert get_response.status_code == 200
    assert get_response.json()["organization_name"] == "Test University"


def test_get_profile_without_profile_created_fails(client, registered_user):
    response = client.get("/api/v1/profile/", headers=registered_user)
    assert response.status_code == 404


def test_get_profile_requires_authentication(client):
    response = client.get("/api/v1/profile/")
    assert response.status_code == 401