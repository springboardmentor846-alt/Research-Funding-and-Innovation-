"""
Automated Integration Test for Phase 3: Funding Opportunity Discovery, Search, AI Recommendations, Bookmarks & Alerts.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.main import create_application
from app.database.session import Base, get_db
from app.services.funding_service import FundingService

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(autouse=True)
async def setup_test_db():
    """Create clean database schema and seed funding data for each test."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        await FundingService.seed_funding_opportunities(session)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app = create_application()
app.dependency_overrides[get_db] = override_get_db


@pytest.mark.asyncio
async def test_phase3_funding_discovery_flow():
    """Test Phase 3: Seeding, Search, Detail, Recommendation, Bookmarking, Alerts."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        # 1. Register & Login User
        reg_res = await ac.post(
            "/api/v1/auth/register",
            json={
                "email": "funding.tester@lab.org",
                "password": "GrantPassword123!",
                "confirm_password": "GrantPassword123!",
                "full_name": "Dr. Funding Tester",
                "role": "researcher",
                "organization": "Quantum AI Institute",
            },
        )
        assert reg_res.status_code == 201

        login_res = await ac.post(
            "/api/v1/auth/login",
            json={"email": "funding.tester@lab.org", "password": "GrantPassword123!"},
        )
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Setup user profile research domains & keywords
        await ac.put(
            "/api/v1/research-profile/me",
            json={
                "research_domains": ["Artificial Intelligence", "Quantum Computing"],
                "keywords": ["Quantum Machine Learning", "Qubits"],
            },
            headers=headers,
        )

        # 2. Search Funding Opportunities (Keyword & Domain)
        search_res = await ac.get(
            "/api/v1/funding/search?q=Quantum&domain=Artificial Intelligence&page=1&page_size=10"
        )
        assert search_res.status_code == 200
        search_data = search_res.json()
        assert search_data["total"] >= 1
        opp_id = search_data["items"][0]["id"]

        # 3. Get Single Opportunity Detail
        detail_res = await ac.get(f"/api/v1/funding/{opp_id}", headers=headers)
        assert detail_res.status_code == 200
        assert detail_res.json()["id"] == opp_id
        assert detail_res.json()["is_bookmarked"] == False

        # 4. Toggle Bookmark
        bm_res = await ac.post(f"/api/v1/funding/{opp_id}/bookmark", headers=headers)
        assert bm_res.status_code == 200
        assert bm_res.json()["bookmarked"] == True

        # Verify in user bookmarks
        bms_res = await ac.get("/api/v1/funding/bookmarks/me", headers=headers)
        assert bms_res.status_code == 200
        assert len(bms_res.json()) >= 1
        assert bms_res.json()[0]["id"] == opp_id

        # 5. Get AI Recommendations
        recs_res = await ac.get("/api/v1/funding/recommendations?limit=5", headers=headers)
        assert recs_res.status_code == 200
        recs = recs_res.json()
        assert len(recs) > 0
        assert "match_score" in recs[0]
        assert recs[0]["match_score"] >= 10.0

        # 6. Dashboard Summary
        dash_res = await ac.get("/api/v1/funding/dashboard-summary", headers=headers)
        assert dash_res.status_code == 200
        dash_data = dash_res.json()
        assert dash_data["saved_grants_count"] == 1
        assert dash_data["total_opportunities_count"] >= 50

        # 7. Create & Delete Alert
        alert_payload = {
            "name": "Quantum AI Grants Alert",
            "keywords": ["Quantum", "Machine Learning"],
            "research_domains": ["Artificial Intelligence"],
            "funding_type": "Grant",
            "frequency": "weekly",
        }
        create_alert_res = await ac.post(
            "/api/v1/funding/alerts", json=alert_payload, headers=headers
        )
        assert create_alert_res.status_code == 201
        alert_id = create_alert_res.json()["id"]

        get_alerts_res = await ac.get("/api/v1/funding/alerts/me", headers=headers)
        assert get_alerts_res.status_code == 200
        assert len(get_alerts_res.json()) == 1

        del_alert_res = await ac.delete(f"/api/v1/funding/alerts/{alert_id}", headers=headers)
        assert del_alert_res.status_code == 204
