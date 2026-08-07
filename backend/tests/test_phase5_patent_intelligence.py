"""
Automated Integration Test for Phase 5: Patent Intelligence Module.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.main import create_application
from app.database.session import Base, get_db
from app.services.patent_service import PatentService

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(autouse=True)
async def setup_test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        await PatentService.seed_patents_and_trends(session)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app = create_application()
app.dependency_overrides[get_db] = override_get_db


@pytest.mark.asyncio
async def test_phase5_patent_intelligence_flow():
    """Test Phase 5: Search, Details, Trends, Analytics, AI Recommendations, and Dashboard Summary."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        # 1. Register & Login User
        reg_res = await ac.post(
            "/api/v1/auth/register",
            json={
                "email": "patent.inventor@quantum.org",
                "password": "PatentPassword123!",
                "confirm_password": "PatentPassword123!",
                "full_name": "Dr. Patent Tester",
                "role": "startup_founder",
                "organization": "Quantum Inventions Inc",
            },
        )
        assert reg_res.status_code == 201

        login_res = await ac.post(
            "/api/v1/auth/login",
            json={"email": "patent.inventor@quantum.org", "password": "PatentPassword123!"},
        )
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Update research profile
        await ac.put(
            "/api/v1/research-profile/me",
            json={
                "research_domains": ["Artificial Intelligence & Machine Learning", "Quantum Computing & Information"],
                "technology_interests": ["Generative AI", "Superconducting Qubits", "Solid-State Batteries"],
                "keywords": ["Transformer Architecture", "Cryo-CMOS", "Matrix Multiplication"],
            },
            headers=headers,
        )

        # 2. Search Patents (Keyword, Domain, Organization, Status, Year)
        search_res = await ac.get(
            "/api/v1/patents/search?q=Transformer&domain=Artificial Intelligence&sort_by=citations_desc&page=1&page_size=10"
        )
        assert search_res.status_code == 200
        search_data = search_res.json()
        assert search_data["total"] >= 1
        patent_id = search_data["items"][0]["id"]

        # 3. Get Patent Details
        detail_res = await ac.get(f"/api/v1/patents/{patent_id}")
        assert detail_res.status_code == 200
        assert detail_res.json()["id"] == patent_id
        assert detail_res.json()["patent_number"].startswith(("US", "EP"))

        # 4. Get Patent Trends
        trend_res = await ac.get("/api/v1/patents/trending?limit=5")
        assert trend_res.status_code == 200
        assert len(trend_res.json()) >= 1
        assert "growth_rate" in trend_res.json()[0]

        # 5. Get Patent Analytics
        analytics_res = await ac.get("/api/v1/patents/analytics")
        assert analytics_res.status_code == 200
        analytics_data = analytics_res.json()
        assert analytics_data["total_patents"] >= 100
        assert len(analytics_data["top_organizations"]) >= 3

        # 6. Get AI Patent Recommendations (with Match Score & Reasoning)
        recs_res = await ac.get("/api/v1/patents/recommendations?limit=5", headers=headers)
        assert recs_res.status_code == 200
        recs = recs_res.json()
        assert len(recs) > 0
        assert recs[0]["match_score"] > 50.0
        assert len(recs[0]["matching_fields"]) > 0
        assert "Recommended with" in recs[0]["recommendation_reason"]

        # 7. Dashboard Summary
        dash_res = await ac.get("/api/v1/patents/dashboard-summary", headers=headers)
        assert dash_res.status_code == 200
        dash_data = dash_res.json()
        assert dash_data["statistics"]["total_patents_indexed"] >= 100
        assert len(dash_data["recent_patents"]) > 0
        assert len(dash_data["top_organizations"]) > 0
