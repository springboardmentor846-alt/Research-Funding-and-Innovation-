import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_register_and_login_user():
    test_email = "testuser2026@platform.ai"
    payload = {
        "email": test_email,
        "password": "Password123!",
        "full_name": "Test User",
        "role": "Researcher",
        "organization": "Test University"
    }
    # Register
    res = client.post("/api/v1/auth/register", json=payload)
    assert res.status_code in [201, 400] # 201 if first time, 400 if already exists

    # Login
    login_payload = {
        "email": test_email,
        "password": "Password123!"
    }
    res_login = client.post("/api/v1/auth/login", json=login_payload)
    assert res_login.status_code == 200
    data = res_login.json()
    assert "access_token" in data
    assert data["user"]["email"] == test_email
