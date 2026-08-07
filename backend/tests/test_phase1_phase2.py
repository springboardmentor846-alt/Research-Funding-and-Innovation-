"""
Automated Integration Test for Phase 1 (Auth & Users) and Phase 2 (Research Profile Management).
Uses SQLite async in-memory database to test all API endpoints in isolation.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.main import create_application
from app.database.session import Base, get_db
from app.core.config import settings

# In-memory SQLite async database for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(autouse=True)
async def setup_test_db():
    """Create clean database schema for each test."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db():
    """Override database dependency to use in-memory SQLite session."""
    async with TestingSessionLocal() as session:
        yield session


app = create_application()
app.dependency_overrides[get_db] = override_get_db


@pytest.mark.asyncio
async def test_phase1_auth_and_user_flow():
    """Test Phase 1: Registration, Login, Current User, Token Refresh."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        # 1. Register User
        reg_payload = {
            "email": "dr.smith@university.edu",
            "password": "StrongPassword123!",
            "confirm_password": "StrongPassword123!",
            "full_name": "Dr. Sarah Smith",
            "role": "researcher",
            "organization": "Stanford University",
        }
        res_reg = await ac.post("/api/v1/auth/register", json=reg_payload)
        assert res_reg.status_code == 201, f"Register failed: {res_reg.text}"
        user_data = res_reg.json()
        assert user_data["email"] == "dr.smith@university.edu"

        # 2. Login User
        login_payload = {
            "email": "dr.smith@university.edu",
            "password": "StrongPassword123!",
        }
        res_login = await ac.post("/api/v1/auth/login", json=login_payload)
        assert res_login.status_code == 200, f"Login failed: {res_login.text}"
        tokens = res_login.json()
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]

        headers = {"Authorization": f"Bearer {access_token}"}

        # 3. Get Current User (/auth/me)
        res_me = await ac.get("/api/v1/auth/me", headers=headers)
        assert res_me.status_code == 200
        assert res_me.json()["full_name"] == "Dr. Sarah Smith"

        # 4. Refresh Token
        res_refresh = await ac.post(
            "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
        )
        assert res_refresh.status_code == 200
        assert "access_token" in res_refresh.json()


@pytest.mark.asyncio
async def test_phase2_research_profile_management():
    """Test Phase 2: Profile Auto-Creation, Profile Update, Publications, Patents, Projects, Search."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        # 1. Register & Login Researcher
        res_reg_2 = await ac.post(
            "/api/v1/auth/register",
            json={
                "email": "prof.quantum@lab.org",
                "password": "QuantumPass123!",
                "confirm_password": "QuantumPass123!",
                "full_name": "Prof. Alan Quantum",
                "role": "researcher",
                "organization": "Quantum Tech Lab",
            },
        )
        assert res_reg_2.status_code == 201, f"Registration failed: {res_reg_2.text}"

        login_res = await ac.post(
            "/api/v1/auth/login",
            json={"email": "prof.quantum@lab.org", "password": "QuantumPass123!"},
        )
        assert login_res.status_code == 200, f"Login failed: {login_res.text}"
        access_token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        # 2. Get My Profile (Verify auto-creation)
        res_prof = await ac.get("/api/v1/research-profile/me", headers=headers)
        assert res_prof.status_code == 200
        profile_data = res_prof.json()
        assert profile_data["full_name"] == "Prof. Alan Quantum"
        profile_id = profile_data["id"]

        # 3. Update Research Profile
        update_payload = {
            "organization_name": "Quantum Research Institute",
            "department": "Department of Physics & Quantum Computing",
            "organization_type": "research_institute",
            "position": "Director of Quantum AI",
            "academic_degree": "Ph.D.",
            "field_of_study": "Quantum Information Systems",
            "institution_name": "MIT",
            "graduation_year": 2018,
            "h_index": 18,
            "i10_index": 24,
            "total_citations": 1450,
            "orcid_id": "0000-0001-9876-5432",
            "research_domains": ["Quantum Computing", "Artificial Intelligence"],
            "keywords": ["Qubits", "Quantum Machine Learning", "Error Correction"],
            "technology_interests": ["Superconducting Qubits", "Photonics"],
            "summary_bio": "Pioneering research in fault-tolerant quantum algorithms and machine learning.",
        }
        res_update = await ac.put(
            "/api/v1/research-profile/me", json=update_payload, headers=headers
        )
        assert res_update.status_code == 200
        updated_profile = res_update.json()
        assert updated_profile["h_index"] == 18
        assert "Quantum Computing" in updated_profile["research_domains"]

        # 4. Add & Update Publication
        pub_payload = {
            "title": "Quantum Supremacy in Machine Learning Benchmarks",
            "venue": "Nature Quantum Information",
            "year": 2024,
            "doi": "10.1038/s41534-024-00123-x",
            "citations_count": 42,
            "authors": "Alan Quantum, Sarah Smith",
            "abstract": "We demonstrate quantum algorithmic speedup in high-dimensional optimization.",
        }
        res_pub = await ac.post(
            "/api/v1/research-profile/me/publications", json=pub_payload, headers=headers
        )
        assert res_pub.status_code == 201
        pub_data = res_pub.json()
        pub_id = pub_data["id"]
        assert pub_data["title"] == pub_payload["title"]

        # Update publication
        res_pub_up = await ac.put(
            f"/api/v1/research-profile/me/publications/{pub_id}",
            json={"citations_count": 50},
            headers=headers,
        )
        assert res_pub_up.status_code == 200
        assert res_pub_up.json()["citations_count"] == 50

        # 5. Add Patent
        patent_payload = {
            "title": "Superconducting Qubit Architecture with Low Cross-Talk",
            "patent_number": "US11894200B2",
            "status": "granted",
            "filing_date": "2022-05-15",
            "issue_date": "2024-01-10",
            "abstract": "A novel topological arrangement of superconducting flux qubits.",
        }
        res_pat = await ac.post(
            "/api/v1/research-profile/me/patents", json=patent_payload, headers=headers
        )
        assert res_pat.status_code == 201
        assert res_pat.json()["patent_number"] == "US11894200B2"

        # 6. Add Research Project
        proj_payload = {
            "title": "Scalable Quantum Machine Learning Platform",
            "role": "Principal Investigator",
            "sponsor_organization": "National Science Foundation (NSF)",
            "funding_amount": 1250000.0,
            "start_date": "2023-09-01",
            "end_date": "2026-08-31",
            "status": "ongoing",
            "summary": "Developing open-source quantum AI software frameworks.",
        }
        res_proj = await ac.post(
            "/api/v1/research-profile/me/projects", json=proj_payload, headers=headers
        )
        assert res_proj.status_code == 201
        assert res_proj.json()["funding_amount"] == 1250000.0

        # 7. Search Researchers Directory
        res_search = await ac.get(
            "/api/v1/research-profile/search?q=Quantum&min_h_index=10"
        )
        assert res_search.status_code == 200
        search_results = res_search.json()
        assert search_results["total"] >= 1
        assert search_results["items"][0]["h_index"] >= 10

        # 8. Public Profile Detail View
        res_public = await ac.get(f"/api/v1/research-profile/{profile_id}")
        assert res_public.status_code == 200
        public_prof = res_public.json()
        assert len(public_prof["publications"]) == 1
        assert len(public_prof["patents"]) == 1
        assert len(public_prof["projects"]) == 1
