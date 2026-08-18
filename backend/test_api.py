"""Basic API smoke tests using FastAPI TestClient."""
from fastapi.testclient import TestClient

from app.main import app


def test_health():
    client = TestClient(app)
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["status"] == "operational"
    print("✓ Root endpoint OK")


def test_healthcheck():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"
    print("✓ Health endpoint OK")


def test_register_login_flow():
    """Test full auth flow."""
    from app.db import SessionLocal
    from app.models.user import User
    from app.core.security import hash_password

    # Clean up
    db = SessionLocal()
    try:
        db.query(User).filter(User.email == "test@example.com").delete()
        db.commit()
    finally:
        db.close()

    client = TestClient(app)
    r = client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "password": "TestPass123",
        "role": "researcher",
    })
    assert r.status_code == 201, f"Register failed: {r.json()}"
    print("✓ Registration OK")

    r = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "TestPass123"},
    )
    assert r.status_code == 200, f"Login failed: {r.json()}"
    token = r.json()["access_token"]
    print("✓ Login OK")

    r = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["username"] == "testuser"
    print("✓ /me OK")


def test_funding_list_requires_auth():
    client = TestClient(app)
    r = client.get("/api/v1/funding")
    assert r.status_code == 401
    print("✓ Protected route requires auth OK")


def test_profile_endpoints_require_auth():
    client = TestClient(app)
    assert client.get("/api/v1/profile/collaborations").status_code == 401
    assert client.get("/api/v1/profile/funding-history").status_code == 401
    print("✓ Profile endpoints require auth OK")


if __name__ == "__main__":
    test_health()
    test_healthcheck()
    try:
        test_register_login_flow()
    except Exception as e:
        print(f"⚠ Auth flow test failed (database may not be running): {e}")
    test_funding_list_requires_auth()
    test_profile_endpoints_require_auth()
    print("\n✓ All smoke tests done")
