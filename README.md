# Research Funding & Innovation Intelligence Platform

A full-stack web platform that helps researchers, startup founders, and innovation managers discover funding opportunities, manage research and patent portfolios, analyze innovation ecosystems, and receive personalized, AI-driven intelligence — all from a single dashboard.

The platform combines researcher profile data with external scholarly, patent, and funding sources, semantic recommendation techniques, and machine learning to turn raw research information into personalized, actionable insight.

---

## Project Overview

Researchers, startups, and innovation managers typically rely on several disconnected tools for funding discovery, publication management, patent research, and ecosystem oversight.

The **Research Funding & Innovation Intelligence Platform** brings these workflows into a single system, with role-specific views for each type of user.

The platform allows users to:

- Create and manage a structured research or startup profile
- Maintain research domains, keywords, technology areas, and organization info
- Manage publications and patents
- Import live scholarly data from OpenAlex and Crossref, and link an ORCID iD
- Discover funding opportunities across 7+ national and international sources
- Receive personalized, semantically-ranked funding and collaborator recommendations
- Estimate grant success probability using a trained ML model
- Chat with an AI assistant for platform guidance
- Explore a live global patent landscape (via Lens.org)
- Find and connect with other researchers and startups, and manage collaboration requests
- Track platform-wide research trends and publication activity
- Oversee the innovation ecosystem as an Innovation Manager
- Administer users and view platform analytics as an Admin

---

## Core Features

### 1. Authentication and Role-Based Access

- User registration and login with JWT access + refresh tokens
- Forgot / reset password via email
- Four roles: **Researcher**, **Startup Founder**, **Innovation Manager**, **Admin**
- Role-based route protection on both frontend and backend
- Request-ID tracing middleware for request logging

### 2. Research Profile Management

- Research profile with domains, keywords, technology areas, and organization information
- Individually manageable research domains, keywords, and technology areas
- Publications and patents, added manually or imported
- ORCID integration to import a researcher's publication record
- Crossref search for publication metadata lookup

### 3. Research Library (OpenAlex Integration)

Researchers can search OpenAlex by topic or keyword and pull in external scholarly work, kept separate from their own authored publications:

- **My Publications** — work the researcher added themselves
- **Research Library** — external scholarly work imported for reference

### 4. Funding Discovery

- Live search of real U.S. federal grants via Grants.gov
- Live search across 7 additional sources: **Horizon Europe, UKRI, ANRF, BIRAC, DBT, ICMR, and Wellcome**
- Keyword search across all stored funding opportunities
- Funding explanation button — plain-language reasoning for why a grant was recommended

### 5. AI Recommendations (Semantic, Embedding-Based)

A TF-IDF + cosine-similarity engine ranks funding opportunities and potential collaborators by how closely their text matches a researcher's profile — catching related concepts (e.g. "machine learning" vs. "artificial intelligence") that exact keyword matching would miss:

```text
Research Profile (domains + keywords + technology areas + organization)
        |
        v
   TF-IDF Vectors
        |
        v
  Cosine Similarity
        |
        v
Ranked Funding Opportunities / Ranked Collaborators
```

This runs alongside the original rule-based domain-matching recommendation used for the "Recommended Funding" list on the Funding tab.

### 6. Grant Success Prediction

A trained scikit-learn model estimates grant success probability from profile and funding features, separate from relevance-based recommendation:

- **Recommendation:** how relevant is this opportunity to the researcher?
- **Prediction:** what is the estimated probability of success?

### 7. AI Assistant (Chatbot)

An in-app assistant (Gemini-backed, with a rule-based knowledge fallback) answers questions about how to use the platform.

### 8. Patent Intelligence

- Global Patent Landscape — live worldwide patent search via Lens.org, with country/applicant/technology aggregation
- Patent trend analysis over time
- Competitor analysis (most active patent holders)
- Technology clustering from patent titles
- Cross-domain Technology Intelligence combining research + patent maturity

### 9. Innovation Scoring & Commercialization

- Weighted Innovation Score based on research, patents, technology, and funding fit
- Commercialization recommendations — actionable next steps derived from a user's innovation profile

### 10. Startup Ecosystem

- Startup profile management (industry, stage, funding stage)
- Find Researchers — startups can discover researchers to collaborate with
- Find Startups — discover other startups on the platform
- Startup-specific funding matching with success prediction

### 11. Collaboration Requests

- Send a collaboration request to any user by ID, with an optional message
- Accept / reject received requests
- Track sent request status (pending / accepted / rejected)

### 12. Research Trends (Platform-Wide)

Aggregated, platform-wide analytics — not tied to a single profile:

- Publications by year (chart)
- Top research domains
- Top keywords (word-cloud-ready)
- Top technology areas

```text
Publication / Profile-Entity Records (all users)
        |
        v
  Aggregation Service
        |
        v
Publications-by-Year · Top Domains · Top Keywords · Top Tech Areas
```

### 13. Dashboard Aggregation

- Personal dashboard — a researcher's own activity snapshot (publications, patents, collaboration requests, startup profile, funding count)
- Platform dashboard — Admin / Innovation Manager view of platform-wide totals

### 14. Innovation Manager Role

A dedicated oversight role and dashboard, separate from Admin:

- Ecosystem Overview — platform-wide totals and role breakdown
- Startup pipeline — all startup profiles with founder contact
- Recent collaboration activity across the platform

### 15. Admin Panel

- Platform Analytics — usage stats across the platform
- User Management — view, search, change role, or delete any user

### 16. Reports

- Export a full innovation intelligence report (PDF / Excel)

### 17. Notifications

- In-app notification bell for account and collaboration events

---

## External Integrations

| Source | Purpose |
|---|---|
| OpenAlex | Scholarly publication discovery and research metadata |
| ORCID | Researcher identity and publication import |
| Crossref | Publication metadata and DOI lookup |
| Lens.org | Global patent search and patent intelligence |
| Grants.gov | Live U.S. federal grant search |
| Horizon Europe, UKRI, ANRF, BIRAC, DBT, ICMR, Wellcome | Additional national/international funding sources |
| Google Gemini | AI Assistant chatbot |

---

## Technology Stack

**Backend**
- Python, FastAPI, Uvicorn
- PostgreSQL (via Docker) + SQLAlchemy ORM
- Alembic for database migrations
- JWT authentication (access + refresh tokens), Passlib for hashing
- Scikit-learn + Joblib (grant prediction, TF-IDF recommendations)
- ReportLab / openpyxl (PDF / Excel report export)
- Pytest for automated testing

**Frontend**
- React (Vite)
- Recharts for data visualization
- Axios for API communication

**DevOps**
- Docker Compose (PostgreSQL containerization)
- GitHub Actions CI — automated backend test suite and frontend build check on every push

---

## Project Architecture

```text
Research-Funding-and-Innovation-/
│
├── .github/
│   └── workflows/
│       ├── backend-tests.yml
│       └── frontend-build.yml
│
├── infra/
│   └── docker-compose.yml
│
├── backend/
│   ├── alembic/
│   └── app/
│       ├── api/
│       │   ├── auth/            (register, login, refresh, password reset)
│       │   ├── profile/         (research profile, domains, keywords, tech areas)
│       │   ├── funding/         (funding opportunities, recommendations)
│       │   ├── collaboration/   (collaboration requests)
│       │   ├── startup/         (startup profile, find researchers/startups)
│       │   ├── chatbot/         (AI assistant)
│       │   ├── dashboard/       (personal + platform dashboards)
│       │   ├── manager/         (Innovation Manager oversight)
│       │   ├── trends/          (platform-wide research trends)
│       │   ├── recommendation/  (semantic AI recommendations)
│       │   └── admin/           (analytics, user management)
│       ├── core/                (config, security / JWT / role checks)
│       ├── crud/
│       ├── db/
│       ├── dependencies/
│       ├── ml/                  (grant prediction model + training script)
│       ├── chatbot/              (assistant knowledge base)
│       ├── models/
│       ├── schemas/
│       ├── services/
│       └── main.py
│   └── tests/
│
├── frontend/
│   └── src/
│       ├── Dashboard.jsx         (role-aware sidebar + tab routing)
│       ├── *Form.jsx, *Search.jsx, *Panel.jsx  (feature components)
│       └── main.jsx / App.jsx
│
├── .gitignore
└── README.md
```

---

## Backend Architecture

### Models — `backend/app/models/`

SQLAlchemy models: `User`, `ResearchProfile`, profile entities (`ResearchDomain`, `ResearchKeyword`, `TechnologyArea`, `OrganizationInformation`), `Publication`, `Patent`, `FundingOpportunity`, `Startup`, `CollaborationRequest`, `PasswordResetToken`.

### API — `backend/app/api/<module>/routes.py`

Each feature area has its own router package, mounted under `/api/v1/<module>` in `main.py`. Routers validate requests, enforce authentication/role checks, and delegate to the service/CRUD layers.

### Services — `backend/app/services/`

```text
email_service.py                 orcid_service.py
crossref_service.py              openalex_service.py
funding_sources_service.py       lens_service.py
grant_prediction_service.py      patent_landscape_service.py
recommendation_service.py        research_trends_service.py
dashboard_service.py             startup_prediction_service.py
chatbot_service.py               explanation_service.py
report_service.py
```

This separation keeps API routing, database models, external integrations, and business logic independent of one another.

### Core — `backend/app/core/`

Configuration and `security.py`, which provides JWT creation/decoding, `get_current_user`, and `require_role([...])` for role-gated endpoints.

---

## Frontend Architecture

The frontend is a single React app (`frontend/src/`) built around one role-aware `Dashboard.jsx` component:

- A sidebar of collapsible tab groups (Workspace, Research, Network, Startup, Patents, Insights, Innovation Manager, Admin), filtered by the logged-in user's role
- Each tab renders a focused, single-purpose component (e.g. `ResearchProfileForm.jsx`, `GlobalPatentLandscape.jsx`, `PlatformTrends.jsx`, `Recommendations.jsx`, `ManagerOverview.jsx`, `AdminPanel.jsx`)
- `AIAssistant.jsx` floats across every view

---

## Application Flow

```text
User
  ↓
React Dashboard (role-aware sidebar)
  ↓
Axios → FastAPI Router (/api/v1/...)
  ↓
Authentication / Role Check (core/security.py)
  ↓
Service / CRUD Layer
  ↓
┌───────────────────────────────┐
│ PostgreSQL                    │
│ OpenAlex · ORCID · Crossref   │
│ Lens.org · Grants.gov · etc.  │
│ Scikit-learn (ML) · Gemini    │
└───────────────────────────────┘
  ↓
FastAPI Response
  ↓
React Dashboard
```

---

## Personalization Architecture

```text
Research Profile
      │
      ├── Domains
      ├── Keywords
      ├── Technology Areas
      └── Organization Info
              ↓
      TF-IDF Researcher Representation
              ↓
      Recommendation / Trends / Prediction Layer
              ↓
 ┌────────────┼────────────┬─────────────┐
 ↓            ↓            ↓             ↓
Funding    Collaborators  Patents    Publications
```

---

## Running the Project Locally

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Research-Funding-and-Innovation-
```

### 2. Start PostgreSQL

```bash
cd infra
docker compose up -d
```

### 3. Backend Setup

```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1      # Windows
pip install -r requirements.txt
```

Create a `.env` file in `backend/` (see `.env.example`), then apply migrations:

```bash
alembic upgrade head
```

Run the backend:

```bash
uvicorn app.main:app --reload
```

- API: `http://127.0.0.1:8000`
- Interactive docs: `http://127.0.0.1:8000/docs`

### 4. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`.

---

## Database Migrations

Alembic manages schema migrations. After changing a SQLAlchemy model:

```bash
alembic revision --autogenerate -m "migration description"
alembic upgrade head
```

---

## Continuous Integration

Two GitHub Actions workflows run on every push and pull request:

- **Backend Tests** (`backend-tests.yml`) — installs backend dependencies and runs the full `pytest` suite
- **Frontend Build** (`frontend-build.yml`) — installs frontend dependencies and runs `npm run build`, catching build-breaking errors before they reach `main`

---

## Security Notes

Never commit sensitive configuration. This includes:

```text
.env
API keys
database passwords
JWT secrets
access tokens
private credentials
```

These are configured via environment variables (`backend/.env`, kept out of git via `.gitignore`).

---

## Current Development Status

Implemented and tested:

- Authentication, password reset, and role-based access (Researcher, Startup Founder, Innovation Manager, Admin)
- Research profile, domains, keywords, technology areas, organization info
- Publication and patent management, ORCID and Crossref integration
- Research Library via OpenAlex
- Funding discovery across 8 sources (Grants.gov + 7 others) with keyword search
- Rule-based and semantic (TF-IDF) funding + collaborator recommendations
- ML-based grant success prediction
- AI Assistant chatbot
- Global Patent Landscape, patent trend, competitor, and technology-cluster analysis
- Innovation scoring and commercialization recommendations
- Startup ecosystem: profiles, discovery, funding matching
- Collaboration requests (send / accept / reject)
- Platform-wide Research Trends analytics
- Personal and platform-wide Dashboard aggregation
- Innovation Manager ecosystem oversight dashboard
- Admin analytics and user management
- PDF / Excel report export and in-app notifications
- Automated backend test suite (104 tests) and CI (backend tests + frontend build) on every push

---

## Project Objective

The objective of this project is to demonstrate how research, patent, and funding information from multiple external sources can be integrated with researcher and startup profiles, semantic recommendation techniques, machine learning, and role-based ecosystem oversight to create a unified **Research Funding and Innovation Intelligence Platform**.

## Author

Upendra