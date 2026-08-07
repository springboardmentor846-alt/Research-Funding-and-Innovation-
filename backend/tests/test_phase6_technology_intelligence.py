"""
Automated Integration Test for Phase 6: Technology Intelligence & Innovation Scoring Module.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.main import create_application
from app.database.session import Base, get_db
from app.services.technology_service import TechnologyService

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
        await TechnologyService.seed_technology_trends(session)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app = create_application()
app.dependency_overrides[get_db] = override_get_db


@pytest.mark.asyncio
async def test_phase6_technology_intelligence_flow():
    """Test Phase 6: Technology Trends Search, Emerging Tech, Innovation Score, Opportunity Analysis, Dashboard Summary."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        # 1. Register & Login User
        reg_res = await ac.post(
            "/api/v1/auth/register",
            json={
                "email": "tech.innovator@lab.org",
                "password": "TechPassword123!",
                "confirm_password": "TechPassword123!",
                "full_name": "Dr. Tech Innovator",
                "role": "innovation_manager",
                "organization": "Future Tech Labs",
            },
        )
        assert reg_res.status_code == 201

        login_res = await ac.post(
            "/api/v1/auth/login",
            json={"email": "tech.innovator@lab.org", "password": "TechPassword123!"},
        )
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Update research profile
        await ac.put(
            "/api/v1/research-profile/me",
            json={
                "research_domains": ["Artificial Intelligence & Machine Learning", "Robotics & Autonomous Systems"],
                "technology_interests": ["Agentic AI", "Neuromorphic Chips", "Humanoid Robotics"],
                "keywords": ["Spiking Neural Nets", "Model Predictive Control", "Sparsification"],
            },
            headers=headers,
        )

        # 2. Search Technology Trends (Keyword, Domain, Maturity Level)
        search_res = await ac.get(
            "/api/v1/technology/trends?q=Agentic&domain=Artificial Intelligence&sort_by=growth_desc&page=1&page_size=10"
        )
        assert search_res.status_code == 200
        search_data = search_res.json()
        assert search_data["total"] >= 1
        trend_id = search_data["items"][0]["id"]

        # 3. Get Single Trend Details
        detail_res = await ac.get(f"/api/v1/technology/trends/{trend_id}")
        assert detail_res.status_code == 200
        assert detail_res.json()["id"] == trend_id
        assert detail_res.json()["trl_level"] >= 1

        # 4. Get Emerging Technologies
        emerging_res = await ac.get("/api/v1/technology/emerging?limit=5")
        assert emerging_res.status_code == 200
        assert len(emerging_res.json()) >= 1
        assert emerging_res.json()[0]["is_emerging"] is True

        # 5. Calculate User Innovation Score
        score_res = await ac.get("/api/v1/technology/innovation-score", headers=headers)
        assert score_res.status_code == 200
        score_data = score_res.json()
        assert score_data["overall_score"] > 0
        assert 1 <= score_data["trl_level"] <= 9
        assert "Your Innovation Index is" in score_data["recommendation_summary"]

        # 6. Opportunity Analysis
        opp_res = await ac.get("/api/v1/technology/opportunities?limit=5", headers=headers)
        assert opp_res.status_code == 200
        opp_data = opp_res.json()
        assert opp_data["total_opportunities"] >= 1
        assert len(opp_data["opportunities"]) > 0

        # 7. Dashboard Summary
        dash_res = await ac.get("/api/v1/technology/dashboard-summary", headers=headers)
        assert dash_res.status_code == 200
        dash_data = dash_res.json()
        assert dash_data["statistics"]["total_trends_indexed"] >= 50
        assert dash_data["innovation_score"]["overall_score"] > 0
        assert len(dash_data["emerging_technologies"]) > 0
