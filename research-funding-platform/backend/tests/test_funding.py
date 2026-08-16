import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_list_funding_opportunities():
    response = client.get("/api/v1/funding")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 0
