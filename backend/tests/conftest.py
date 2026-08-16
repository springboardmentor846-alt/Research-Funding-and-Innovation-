import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.db.database import Base, get_db
from app.core.limiter import limiter

# Rate limiting is disabled during tests since the test suite calls
# register/login far more often than a real user would in one minute.
# The actual rate limits are still enforced when the app runs normally.
limiter.enabled = False

# Isolated in-memory SQLite database used only for tests.
# This never touches the real PostgreSQL database used by the app.
TEST_DATABASE_URL = "sqlite:///./test_pytest.db"

engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown_db():
    """Creates all tables before each test and drops them after,
    so every test starts from a clean, empty database."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def registered_user(client):
    """Registers and logs in a test researcher account.
    Returns the auth headers ready to use in requests."""
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test User",
            "email": "pytest_user@example.com",
            "password": "testpass123",
            "role": "researcher",
        },
    )
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "pytest_user@example.com", "password": "testpass123"},
    )
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_user(client):
    """Registers and logs in a test admin account."""
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test Admin",
            "email": "pytest_admin@example.com",
            "password": "adminpass123",
            "role": "admin",
        },
    )
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "pytest_admin@example.com", "password": "adminpass123"},
    )
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}