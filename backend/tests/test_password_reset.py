def test_forgot_password_unknown_email_returns_generic_message(client):
    response = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "doesnotexist@example.com"},
    )
    assert response.status_code == 200
    assert "password reset link" in response.json()["message"].lower()


def test_forgot_password_known_email_creates_token_and_resets_password(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Reset User",
            "email": "reset_user@example.com",
            "password": "oldpassword123",
            "role": "researcher",
        },
    )

    from app.crud.user import get_user_by_email
    from app.main import app
    from app.db.database import get_db

    # Use the overridden test session (conftest overrides get_db already)
    db_gen = app.dependency_overrides[get_db]()
    db = next(db_gen)

    response = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "reset_user@example.com"},
    )
    assert response.status_code == 200

    user = get_user_by_email(db, "reset_user@example.com")
    assert user is not None

    from app.models.password_reset_token import PasswordResetToken
    token_row = (
        db.query(PasswordResetToken)
        .filter(PasswordResetToken.user_id == user.id)
        .order_by(PasswordResetToken.id.desc())
        .first()
    )
    assert token_row is not None

    reset_response = client.post(
        "/api/v1/auth/reset-password",
        json={"token": token_row.token, "new_password": "newpassword123"},
    )
    assert reset_response.status_code == 200

    login_old = client.post(
        "/api/v1/auth/login",
        json={"email": "reset_user@example.com", "password": "oldpassword123"},
    )
    assert login_old.status_code == 401

    login_new = client.post(
        "/api/v1/auth/login",
        json={"email": "reset_user@example.com", "password": "newpassword123"},
    )
    assert login_new.status_code == 200


def test_reset_password_with_invalid_token_fails(client):
    response = client.post(
        "/api/v1/auth/reset-password",
        json={"token": "not-a-real-token", "new_password": "whatever123"},
    )
    assert response.status_code == 400