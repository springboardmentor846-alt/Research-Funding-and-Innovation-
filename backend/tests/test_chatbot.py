def test_chatbot_requires_auth(client):
    response = client.post("/api/v1/chatbot/ask", json={"message": "How do I add a publication?"})
    assert response.status_code == 401


def test_chatbot_without_api_key_returns_clear_error_not_crash(client, registered_user):
    """
    Without GEMINI_API_KEY configured (the default for local/test runs),
    the chatbot must respond with a clear 503 error rather than crashing
    the server or the test suite.
    """
    response = client.post(
        "/api/v1/chatbot/ask",
        json={"message": "How do I add a publication?"},
        headers=registered_user,
    )
    assert response.status_code in (503, 200)
    if response.status_code == 503:
        assert "GEMINI_API_KEY" in response.json()["detail"]


def test_chatbot_validates_empty_message(client, registered_user):
    response = client.post(
        "/api/v1/chatbot/ask",
        json={"message": ""},
        headers=registered_user,
    )
    assert response.status_code == 422 