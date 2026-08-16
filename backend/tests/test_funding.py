def test_add_funding_requires_admin_role(client, registered_user):
    response = client.post(
        "/api/v1/funding/",
        json={"title": "AI Grant", "source": "NSF", "domains": "AI"},
        headers=registered_user,
    )
    assert response.status_code == 403


def test_add_funding_as_admin_succeeds(client, admin_user):
    response = client.post(
        "/api/v1/funding/",
        json={"title": "AI Grant", "source": "NSF", "domains": "AI"},
        headers=admin_user,
    )
    assert response.status_code == 200
    assert response.json()["title"] == "AI Grant"


def test_list_funding_is_public(client, admin_user):
    client.post(
        "/api/v1/funding/",
        json={"title": "Blockchain Grant", "source": "DOE", "domains": "Blockchain"},
        headers=admin_user,
    )
    response = client.get("/api/v1/funding/")
    assert response.status_code == 200
    titles = [f["title"] for f in response.json()]
    assert "Blockchain Grant" in titles


def test_get_funding_not_found(client):
    response = client.get("/api/v1/funding/9999")
    assert response.status_code == 404