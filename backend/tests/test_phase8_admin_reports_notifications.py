"""
Automated Integration Test for Phase 8: Reports, Notifications, Admin Dashboard, and User Management Module.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.main import create_application
from app.database.session import Base, get_db
from app.services.reports_notifications_service import ReportsNotificationsService
from app.services.commercialization_service import CommercializationService
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
async def test_phase8_admin_reports_notifications_flow():
    """Test Phase 8: Notifications, Reports Generation, CSV Export, Admin Stats, System Analytics, and User Management."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        # 1. Register Admin User
        reg_res = await ac.post(
            "/api/v1/auth/register",
            json={
                "email": "admin.master@rfip.org",
                "password": "AdminPassword123!",
                "confirm_password": "AdminPassword123!",
                "full_name": "Admin Director",
                "role": "administrator",
                "organization": "RFIP Platform Admin",
            },
        )
        assert reg_res.status_code == 201
        user_id = reg_res.json()["id"]

        login_res = await ac.post(
            "/api/v1/auth/login",
            json={"email": "admin.master@rfip.org", "password": "AdminPassword123!"},
        )
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Seed sample notifications
        async with TestingSessionLocal() as session:
            await ReportsNotificationsService.seed_sample_data(session)

        # 2. Get Notifications
        notif_res = await ac.get("/api/v1/notifications", headers=headers)
        assert notif_res.status_code == 200
        notifs_data = notif_res.json()
        assert len(notifs_data["notifications"]) >= 1
        notif_id = notifs_data["notifications"][0]["id"]

        # 3. Mark Notification Read & Read All
        read_res = await ac.post(f"/api/v1/notifications/{notif_id}/read", headers=headers)
        assert read_res.status_code == 200
        assert read_res.json()["is_read"] is True

        read_all_res = await ac.post("/api/v1/notifications/read-all", headers=headers)
        assert read_all_res.status_code == 200
        assert read_all_res.json()["unread_count"] == 0

        # 4. Generate Reports (Research Summary, Funding, Patent, Innovation Score)
        report_req = await ac.post(
            "/api/v1/reports/generate",
            json={"report_type": "research_summary", "title": "Quarterly Research Performance Report", "format": "pdf"},
            headers=headers,
        )
        assert report_req.status_code == 201
        assert report_req.json()["report_type"] == "research_summary"

        list_reports = await ac.get("/api/v1/reports", headers=headers)
        assert list_reports.status_code == 200
        assert len(list_reports.json()) >= 1

        # 5. Export Report CSV
        csv_res = await ac.get("/api/v1/reports/export/csv/funding", headers=headers)
        assert csv_res.status_code == 200
        assert "text/csv" in csv_res.headers["content-type"]
        assert "Title" in csv_res.text

        # 6. Admin Dashboard Statistics
        stats_res = await ac.get("/api/v1/admin/stats", headers=headers)
        assert stats_res.status_code == 200
        stats = stats_res.json()
        assert stats["total_users"] >= 1
        assert stats["commercialization_opportunities"] >= 10

        # 7. System Analytics
        analytics_res = await ac.get("/api/v1/admin/analytics", headers=headers)
        assert analytics_res.status_code == 200
        analytics = analytics_res.json()
        assert len(analytics["user_growth"]) > 0
        assert len(analytics["domain_distribution"]) > 0

        # 8. User Management APIs
        users_res = await ac.get("/api/v1/admin/users", headers=headers)
        assert users_res.status_code == 200
        assert len(users_res.json()) >= 1

        status_update = await ac.put(
            f"/api/v1/admin/users/{user_id}/status",
            json={"is_active": True, "role": "administrator"},
            headers=headers,
        )
        assert status_update.status_code == 200
        assert status_update.json()["role"] == "administrator"
