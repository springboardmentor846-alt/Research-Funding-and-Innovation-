def test_register_new_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Alice",
            "email": "alice@example.com",
            "password": "securepass",
            "role": "researcher",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "alice@example.com"
    assert body["message"] == "User registered successfully"


def test_register_duplicate_email_fails(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Alice",
            "email": "alice@example.com",
            "password": "securepass",
            "role": "researcher",
        },
    )
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Alice Again",
            "email": "alice@example.com",
            "password": "anotherpass",
            "role": "researcher",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_login_success(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Bob",
            "email": "bob@example.com",
            "password": "mypassword",
            "role": "researcher",
        },
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "bob@example.com", "password": "mypassword"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["email"] == "bob@example.com"
    assert body["role"] == "researcher"


def test_login_wrong_password_fails(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Bob",
            "email": "bob@example.com",
            "password": "mypassword",
            "role": "researcher",
        },
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "bob@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid password"


def test_login_nonexistent_user_fails(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "whatever"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "User not found"


def test_refresh_token_success(client, registered_user):
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "pytest_user@example.com", "password": "testpass123"},
    )
    refresh_token = login_res.json()["refresh_token"]

    response = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_refresh_token_missing_fails(client):
    response = client.post("/api/v1/auth/refresh", json={})
    assert response.status_code == 400


def test_get_me_requires_authentication(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_get_me_with_valid_token(client, registered_user):
    response = client.get("/api/v1/auth/me", headers=registered_user)
    assert response.status_code == 200
    assert response.json()["email"] == "pytest_user@example.com"