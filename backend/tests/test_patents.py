def _create_profile(client, headers):
    client.post(
        "/api/v1/profile/",
        json={"research_domains": "AI", "organization_name": "Test University"},
        headers=headers,
    )


def test_add_patent_without_profile_fails(client, registered_user):
    response = client.post(
        "/api/v1/profile/patents",
        json={"title": "Patent A", "assignee": "Test Corp"},
        headers=registered_user,
    )
    assert response.status_code == 404


def test_add_and_list_patents(client, registered_user):
    _create_profile(client, registered_user)

    add_response = client.post(
        "/api/v1/profile/patents",
        json={
            "title": "Blockchain Validation Method",
            "assignee": "Test Corp",
            "filing_date": "2024-01-01",
            "patent_number": "US1234567",
        },
        headers=registered_user,
    )
    assert add_response.status_code == 200
    assert add_response.json()["patent_number"] == "US1234567"

    list_response = client.get("/api/v1/profile/patents", headers=registered_user)
    assert list_response.status_code == 200
    numbers = [p["patent_number"] for p in list_response.json()]
    assert "US1234567" in numbers


def test_patent_trend_endpoint(client, registered_user):
    _create_profile(client, registered_user)
    client.post(
        "/api/v1/profile/patents",
        json={"title": "Patent A", "assignee": "X", "filing_date": "2024-05-01"},
        headers=registered_user,
    )
    response = client.get("/api/v1/profile/patents/trend")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_competitor_analysis_endpoint(client, registered_user):
    _create_profile(client, registered_user)
    client.post(
        "/api/v1/profile/patents",
        json={"title": "Patent A", "assignee": "Google LLC"},
        headers=registered_user,
    )
    response = client.get("/api/v1/profile/patents/competitor-analysis")
    assert response.status_code == 200
    assignees = [c["assignee"] for c in response.json()]
    assert "Google LLC" in assignees