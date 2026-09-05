def _register_and_login(client, email, role="researcher"):
    client.post(
        "/api/v1/auth/register",
        json={"name": email.split("@")[0], "email": email, "password": "password123", "role": role},
    )
    login = client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_send_collaboration_request_requires_auth(client):
    response = client.post("/api/v1/collaboration/", json={"receiver_id": 1, "message": "hi"})
    assert response.status_code == 401


def test_send_and_respond_to_collaboration_request(client):
    sender_headers = _register_and_login(client, "sender@example.com", role="researcher")
    receiver_headers = _register_and_login(client, "receiver@example.com", role="startup")

    me_response = client.get("/api/v1/auth/me", headers=receiver_headers)
    assert me_response.status_code == 200

    from app.crud.user import get_user_by_email
    from app.main import app
    from app.db.database import get_db

    db = next(app.dependency_overrides[get_db]())
    receiver_user = get_user_by_email(db, "receiver@example.com")

    send_response = client.post(
        "/api/v1/collaboration/",
        json={"receiver_id": receiver_user.id, "message": "Let's collaborate"},
        headers=sender_headers,
    )
    assert send_response.status_code == 200
    request_id = send_response.json()["id"]
    assert send_response.json()["status"] == "pending"

    received = client.get("/api/v1/collaboration/received", headers=receiver_headers)
    assert received.status_code == 200
    assert any(r["id"] == request_id for r in received.json())

    respond = client.patch(
        f"/api/v1/collaboration/{request_id}",
        json={"status": "accepted"},
        headers=receiver_headers,
    )
    assert respond.status_code == 200
    assert respond.json()["status"] == "accepted"


def test_cannot_respond_to_someone_elses_request(client):
    sender_headers = _register_and_login(client, "sender2@example.com")
    receiver_headers = _register_and_login(client, "receiver2@example.com")
    outsider_headers = _register_and_login(client, "outsider@example.com")

    from app.crud.user import get_user_by_email
    from app.main import app
    from app.db.database import get_db

    db = next(app.dependency_overrides[get_db]())
    receiver_user = get_user_by_email(db, "receiver2@example.com")

    send_response = client.post(
        "/api/v1/collaboration/",
        json={"receiver_id": receiver_user.id},
        headers=sender_headers,
    )
    request_id = send_response.json()["id"]

    respond = client.patch(
        f"/api/v1/collaboration/{request_id}",
        json={"status": "accepted"},
        headers=outsider_headers,
    )
    assert respond.status_code == 403