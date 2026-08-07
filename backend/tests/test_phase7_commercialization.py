"""
Automated Integration Test for Phase 7: Commercialization & Industry Collaboration Module.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.main import create_application
from app.database.session import Base, get_db
from app.services.commercialization_service import CommercializationService

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
        await CommercializationService.seed_commercialization_data(session)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app = create_application()
app.dependency_overrides[get_db] = override_get_db


@pytest.mark.asyncio
async def test_phase7_commercialization_flow():
    """Test Phase 7: Opportunities Search, Details, Industry Partners, Startup Programs, Bookmarks, Collaboration Requests, AI Recommendations, Dashboard Summary."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        # 1. Register & Login User
        reg_res = await ac.post(
            "/api/v1/auth/register",
            json={
                "email": "comm.partner@tech.org",
                "password": "CommPassword123!",
                "confirm_password": "CommPassword123!",
                "full_name": "Dr. Commercial Partner",
                "role": "startup_founder",
                "organization": "Quantum Bio Spinout Inc",
            },
        )
        assert reg_res.status_code == 201

        login_res = await ac.post(
            "/api/v1/auth/login",
            json={"email": "comm.partner@tech.org", "password": "CommPassword123!"},
        )
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Update research profile
        await ac.put(
            "/api/v1/research-profile/me",
            json={
                "research_domains": ["Artificial Intelligence & Machine Learning", "Biotechnology & Genomics"],
                "technology_interests": ["Transformer Compression", "Targeted LNP", "Gene Editing"],
                "keywords": ["Sparsification", "mRNA Delivery", "CRISPR Base Editing"],
            },
            headers=headers,
        )

        # 2. Search Commercialization Opportunities (Keyword, Domain, Opportunity Type)
        search_res = await ac.get(
            "/api/v1/commercialization/opportunities?q=Licensing&domain=Artificial Intelligence&sort_by=created_desc&page=1&page_size=10"
        )
        assert search_res.status_code == 200
        search_data = search_res.json()
        assert search_data["total"] >= 1
        opp_id = search_data["items"][0]["id"]

        # 3. Get Single Opportunity Details
        detail_res = await ac.get(f"/api/v1/commercialization/opportunities/{opp_id}")
        assert detail_res.status_code == 200
        assert detail_res.json()["id"] == opp_id

        # 4. Get Industry Partners Directory
        partners_res = await ac.get("/api/v1/commercialization/partners")
        assert partners_res.status_code == 200
        assert len(partners_res.json()) >= 1
        assert "organization_type" in partners_res.json()[0]

        # 5. Get Startup Programs & Accelerators
        startups_res = await ac.get("/api/v1/commercialization/startup-programs")
        assert startups_res.status_code == 200
        assert len(startups_res.json()) >= 1

        # 6. Toggle Bookmark
        bm_res = await ac.post(f"/api/v1/commercialization/bookmarks/{opp_id}", headers=headers)
        assert bm_res.status_code == 200
        assert bm_res.json()["is_bookmarked"] is True

        # 7. Submit Collaboration Interest Request
        collab_res = await ac.post(
            f"/api/v1/commercialization/collaborate/{opp_id}",
            json={"status": "contacted", "message": "We would like to discuss licensing your transformer patent portfolio."},
            headers=headers,
        )
        assert collab_res.status_code == 200
        assert collab_res.json()["status"] == "contacted"

        # 8. Get AI Recommendations
        recs_res = await ac.get("/api/v1/commercialization/recommendations?limit=5", headers=headers)
        assert recs_res.status_code == 200
        recs = recs_res.json()
        assert len(recs) > 0
        assert recs[0]["match_score"] > 50.0
        assert "suggested_industry_partner" in recs[0]

        # 9. Dashboard Summary
        dash_res = await ac.get("/api/v1/commercialization/dashboard-summary", headers=headers)
        assert dash_res.status_code == 200
        dash_data = dash_res.json()
        assert dash_data["statistics"]["total_opportunities"] >= 10
        assert len(dash_data["recommended_opportunities"]) > 0
        assert len(dash_data["industry_partners"]) > 0
