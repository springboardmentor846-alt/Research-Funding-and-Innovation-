def _create_profile(client, headers):
    return client.post(
        "/api/v1/profile/",
        json={"organization_name": "Test University"},
        headers=headers,
    )


# ---------------- Research Domains ----------------

def test_add_and_list_domain(client, registered_user):
    _create_profile(client, registered_user)

    add_response = client.post(
        "/api/v1/profile/domains", json={"name": "AI"}, headers=registered_user
    )
    assert add_response.status_code == 200
    assert add_response.json()["name"] == "AI"

    list_response = client.get("/api/v1/profile/domains", headers=registered_user)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1


def test_duplicate_domain_rejected(client, registered_user):
    _create_profile(client, registered_user)
    client.post("/api/v1/profile/domains", json={"name": "AI"}, headers=registered_user)
    duplicate = client.post("/api/v1/profile/domains", json={"name": "AI"}, headers=registered_user)
    assert duplicate.status_code == 400


def test_delete_domain_and_sync_updates_profile(client, registered_user):
    _create_profile(client, registered_user)
    add_response = client.post(
        "/api/v1/profile/domains", json={"name": "Robotics"}, headers=registered_user
    )
    domain_id = add_response.json()["id"]

    # Adding a domain should sync into the profile's comma-separated field
    profile = client.get("/api/v1/profile/", headers=registered_user).json()
    assert "Robotics" in profile["research_domains"]

    delete_response = client.delete(f"/api/v1/profile/domains/{domain_id}", headers=registered_user)
    assert delete_response.status_code == 200

    profile_after = client.get("/api/v1/profile/", headers=registered_user).json()
    assert "Robotics" not in (profile_after["research_domains"] or "")


# ---------------- Research Keywords ----------------

def test_add_list_delete_keyword(client, registered_user):
    _create_profile(client, registered_user)

    add_response = client.post(
        "/api/v1/profile/keywords", json={"name": "deep learning"}, headers=registered_user
    )
    assert add_response.status_code == 200
    keyword_id = add_response.json()["id"]

    list_response = client.get("/api/v1/profile/keywords", headers=registered_user)
    assert len(list_response.json()) == 1

    delete_response = client.delete(f"/api/v1/profile/keywords/{keyword_id}", headers=registered_user)
    assert delete_response.status_code == 200

    list_after = client.get("/api/v1/profile/keywords", headers=registered_user)
    assert len(list_after.json()) == 0


# ---------------- Technology Areas ----------------

def test_add_list_delete_technology_area(client, registered_user):
    _create_profile(client, registered_user)

    add_response = client.post(
        "/api/v1/profile/technology-areas", json={"name": "Neural Networks"}, headers=registered_user
    )
    assert add_response.status_code == 200
    tech_id = add_response.json()["id"]

    list_response = client.get("/api/v1/profile/technology-areas", headers=registered_user)
    assert len(list_response.json()) == 1

    delete_response = client.delete(f"/api/v1/profile/technology-areas/{tech_id}", headers=registered_user)
    assert delete_response.status_code == 200


def test_domains_keywords_require_profile(client, registered_user):
    response = client.post("/api/v1/profile/domains", json={"name": "AI"}, headers=registered_user)
    assert response.status_code == 404


# ---------------- Organization Information ----------------

def test_organization_info_not_set_initially(client, registered_user):
    _create_profile(client, registered_user)
    response = client.get("/api/v1/profile/organization-info", headers=registered_user)
    assert response.status_code == 404


def test_set_and_get_organization_info(client, registered_user):
    _create_profile(client, registered_user)

    update_response = client.put(
        "/api/v1/profile/organization-info",
        json={
            "department": "Computer Science",
            "organization_type": "University",
            "city": "Delhi",
            "country": "India",
        },
        headers=registered_user,
    )
    assert update_response.status_code == 200
    assert update_response.json()["department"] == "Computer Science"

    get_response = client.get("/api/v1/profile/organization-info", headers=registered_user)
    assert get_response.status_code == 200
    assert get_response.json()["city"] == "Delhi"


# ---------------- Admin: role update + delete ----------------

def test_update_user_role_requires_admin(client, registered_user):
    response = client.patch(
        "/api/v1/admin/users/1/role", json={"role": "admin"}, headers=registered_user
    )
    assert response.status_code == 403


def test_admin_can_update_user_role(client, registered_user, admin_user):
    me_response = client.get("/api/v1/auth/me", headers=registered_user)
    email = me_response.json()["email"]

    users = client.get("/api/v1/admin/users", headers=admin_user).json()
    target_user = next(u for u in users if u["email"] == email)

    update_response = client.patch(
        f"/api/v1/admin/users/{target_user['id']}/role",
        json={"role": "startup_founder"},
        headers=admin_user,
    )
    assert update_response.status_code == 200
    assert update_response.json()["role"] == "startup_founder"


def test_admin_rejects_invalid_role(client, admin_user):
    users = client.get("/api/v1/admin/users", headers=admin_user).json()
    any_user = users[0]

    response = client.patch(
        f"/api/v1/admin/users/{any_user['id']}/role",
        json={"role": "not-a-real-role"},
        headers=admin_user,
    )
    assert response.status_code == 400


def test_admin_can_delete_user(client, admin_user):
    client.post(
        "/api/v1/auth/register",
        json={"name": "ToDelete", "email": "todelete@example.com", "password": "password123", "role": "researcher"},
    )
    users = client.get("/api/v1/admin/users", headers=admin_user).json()
    target = next(u for u in users if u["email"] == "todelete@example.com")

    delete_response = client.delete(f"/api/v1/admin/users/{target['id']}", headers=admin_user)
    assert delete_response.status_code == 200

    users_after = client.get("/api/v1/admin/users", headers=admin_user).json()
    assert not any(u["email"] == "todelete@example.com" for u in users_after)


def test_admin_users_search_filter(client, admin_user):
    client.post(
        "/api/v1/auth/register",
        json={"name": "Findme", "email": "findme_unique@example.com", "password": "password123", "role": "researcher"},
    )
    response = client.get("/api/v1/admin/users", params={"search": "findme_unique"}, headers=admin_user)
    assert response.status_code == 200
    assert len(response.json()) == 1