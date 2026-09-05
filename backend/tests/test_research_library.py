def _create_profile(client, headers):
    client.post(
        "/api/v1/profile/",
        json={"research_domains": "AI", "organization_name": "Test University"},
        headers=headers,
    )


def test_library_starts_empty(client, registered_user):
    _create_profile(client, registered_user)
    response = client.get("/api/v1/profile/library", headers=registered_user)
    assert response.status_code == 200
    assert response.json() == []


def test_add_to_library_does_not_appear_in_my_publications(client, registered_user):
    _create_profile(client, registered_user)

    add_response = client.post(
        "/api/v1/profile/library",
        json={
            "title": "An External Paper",
            "authors": "Someone Else",
            "year": "2023",
            "source": "Nature",
            "link": "https://example.com/paper",
        },
        headers=registered_user,
    )
    assert add_response.status_code == 200
    assert add_response.json()["source_type"] == "external"

    library = client.get("/api/v1/profile/library", headers=registered_user)
    assert len(library.json()) == 1
    assert library.json()[0]["title"] == "An External Paper"

    my_pubs = client.get("/api/v1/profile/publications", headers=registered_user)
    assert my_pubs.json() == []


def test_own_publication_not_in_library(client, registered_user):
    _create_profile(client, registered_user)

    client.post(
        "/api/v1/profile/publications",
        json={"title": "My Own Paper", "year": "2024"},
        headers=registered_user,
    )

    library = client.get("/api/v1/profile/library", headers=registered_user)
    assert library.json() == []

    my_pubs = client.get("/api/v1/profile/publications", headers=registered_user)
    assert len(my_pubs.json()) == 1
    assert my_pubs.json()[0]["source_type"] == "own"


def test_upload_pdf_to_own_publication(client, registered_user):
    _create_profile(client, registered_user)

    add_response = client.post(
        "/api/v1/profile/publications",
        json={"title": "Paper With PDF", "year": "2024"},
        headers=registered_user,
    )
    pub_id = add_response.json()["id"]

    fake_pdf = b"%PDF-1.4 fake content"
    upload_response = client.post(
        f"/api/v1/profile/publications/{pub_id}/upload-pdf",
        files={"file": ("paper.pdf", fake_pdf, "application/pdf")},
        headers=registered_user,
    )
    assert upload_response.status_code == 200
    assert upload_response.json()["pdf_path"] is not None
    assert upload_response.json()["pdf_path"].endswith(".pdf")


def test_upload_non_pdf_rejected(client, registered_user):
    _create_profile(client, registered_user)

    add_response = client.post(
        "/api/v1/profile/publications",
        json={"title": "Paper Without PDF", "year": "2024"},
        headers=registered_user,
    )
    pub_id = add_response.json()["id"]

    upload_response = client.post(
        f"/api/v1/profile/publications/{pub_id}/upload-pdf",
        files={"file": ("notes.txt", b"just text", "text/plain")},
        headers=registered_user,
    )
    assert upload_response.status_code == 400