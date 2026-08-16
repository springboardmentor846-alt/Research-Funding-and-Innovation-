def _create_profile(client, headers):
    client.post(
        "/api/v1/profile/",
        json={"research_domains": "AI", "organization_name": "Test University"},
        headers=headers,
    )


def test_add_publication_without_profile_fails(client, registered_user):
    response = client.post(
        "/api/v1/profile/publications",
        json={"title": "A Paper", "authors": "A. Author", "year": "2024"},
        headers=registered_user,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Create your research profile first"


def test_add_and_list_publications(client, registered_user):
    _create_profile(client, registered_user)

    add_response = client.post(
        "/api/v1/profile/publications",
        json={
            "title": "Deep Learning for Everyone",
            "authors": "A. Author, B. Author",
            "year": "2024",
            "source": "IEEE",
        },
        headers=registered_user,
    )
    assert add_response.status_code == 200
    assert add_response.json()["title"] == "Deep Learning for Everyone"

    list_response = client.get("/api/v1/profile/publications", headers=registered_user)
    assert list_response.status_code == 200
    titles = [p["title"] for p in list_response.json()]
    assert "Deep Learning for Everyone" in titles


def test_list_publications_without_profile_returns_empty(client, registered_user):
    response = client.get("/api/v1/profile/publications", headers=registered_user)
    assert response.status_code == 200
    assert response.json() == []