"""
Automated Integration Test for Phase 4: Research Intelligence Module.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.main import create_application
from app.database.session import Base, get_db
from app.services.research_intelligence_service import ResearchIntelligenceService

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
        await ResearchIntelligenceService.seed_research_papers_and_trends(session)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app = create_application()
app.dependency_overrides[get_db] = override_get_db


@pytest.mark.asyncio
async def test_phase4_research_intelligence_flow():
    """Test Phase 4: Paper Search, Recommendations, Trending, Emerging, Detail, Dashboard Summary."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        # 1. Register & Login User
        reg_res = await ac.post(
            "/api/v1/auth/register",
            json={
                "email": "intel.tester@lab.org",
                "password": "PaperPassword123!",
                "confirm_password": "PaperPassword123!",
                "full_name": "Dr. Intel Tester",
                "role": "researcher",
                "organization": "Quantum AI Lab",
            },
        )
        assert reg_res.status_code == 201

        login_res = await ac.post(
            "/api/v1/auth/login",
            json={"email": "intel.tester@lab.org", "password": "PaperPassword123!"},
        )
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Update research profile
        await ac.put(
            "/api/v1/research-profile/me",
            json={
                "research_domains": ["Quantum Computing", "Artificial Intelligence"],
                "keywords": ["Quantum Machine Learning", "Qubits", "Diffusion Models"],
            },
            headers=headers,
        )

        # 2. Search Papers (Keyword, Domain, Year Range, Author)
        search_res = await ac.get(
            "/api/v1/research-intelligence/search?q=Quantum&domain=Quantum Computing&year_min=2020&sort_by=citations_desc&page=1&page_size=10"
        )
        assert search_res.status_code == 200
        search_data = search_res.json()
        assert search_data["total"] >= 1
        paper_id = search_data["items"][0]["id"]

        # 3. Get Paper Details
        detail_res = await ac.get(f"/api/v1/research-intelligence/papers/{paper_id}")
        assert detail_res.status_code == 200
        assert detail_res.json()["id"] == paper_id

        # 4. Get Trending Research & Emerging Topics
        trend_res = await ac.get("/api/v1/research-intelligence/trending?limit=5")
        assert trend_res.status_code == 200
        assert len(trend_res.json()) >= 1

        emerging_res = await ac.get("/api/v1/research-intelligence/emerging?limit=5")
        assert emerging_res.status_code == 200
        assert len(emerging_res.json()) >= 1

        # 5. Get AI Recommendations with Matching Reasons
        recs_res = await ac.get("/api/v1/research-intelligence/recommendations?limit=5", headers=headers)
        assert recs_res.status_code == 200
        recs = recs_res.json()
        assert len(recs) > 0
        assert "match_score" in recs[0]
        assert "matching_reason" in recs[0]
        assert len(recs[0]["matching_reason"]) > 5

        # 6. Dashboard Summary
        dash_res = await ac.get("/api/v1/research-intelligence/dashboard-summary", headers=headers)
        assert dash_res.status_code == 200
        dash_data = dash_res.json()
        assert dash_data["statistics"]["total_papers_indexed"] >= 100
