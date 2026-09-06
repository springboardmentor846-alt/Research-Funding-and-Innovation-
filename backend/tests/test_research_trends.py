def test_trends_require_auth(client):
    response = client.get("/api/v1/trends/overview")
    assert response.status_code == 401


def test_trends_overview_empty_platform(client, registered_user):
    response = client.get("/api/v1/trends/overview", headers=registered_user)
    assert response.status_code == 200
    body = response.json()
    assert body == {
        "publications_by_year": [],
        "top_domains": [],
        "top_keywords": [],
        "top_technology_areas": [],
    }


def test_trends_reflect_profile_and_publication_data(client, registered_user):
    client.post(
        "/api/v1/profile/",
        json={"research_domains": "Artificial Intelligence", "keywords": "nlp, transformers"},
        headers=registered_user,
    )
    client.post(
        "/api/v1/profile/domains",
        json={"name": "Artificial Intelligence"},
        headers=registered_user,
    )
    client.post(
        "/api/v1/profile/keywords",
        json={"name": "transformers"},
        headers=registered_user,
    )
    client.post(
        "/api/v1/profile/publications",
        json={"title": "A paper on transformers", "authors": "Test User", "year": "2024"},
        headers=registered_user,
    )

    response = client.get("/api/v1/trends/overview", headers=registered_user)
    assert response.status_code == 200
    body = response.json()

    assert {"year": "2024", "count": 1} in body["publications_by_year"]
    assert any(d["name"] == "Artificial Intelligence" for d in body["top_domains"])
    assert any(k["name"] == "transformers" for k in body["top_keywords"])