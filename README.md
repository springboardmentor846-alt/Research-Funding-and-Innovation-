# AI-Powered Research Funding & Innovation Intelligence Platform

An AI-driven platform designed to assist researchers, startup founders, universities, and enterprise R&D teams in identifying relevant funding opportunities, analyzing global research trends, and evaluating innovation landscapes.

---

## Project Overview & Approach

The **Research Funding & Innovation Intelligence Platform** bridges the gap between academic research, open innovation data, and funding opportunities. By integrating bibliographic datasets with custom matching algorithms, the platform streamlines how researchers and entrepreneurs discover grants, track domain trends, and make data-driven decisions.

### Core Approach
1. **Profile-Driven Recommendations**: User profiles (domains, keywords, role, region) are dynamically matched against active funding programs using weighted scoring heuristics.
2. **Real-time Trend Analytics**: Live academic research data is retrieved and processed to visualize publication trajectories, sub-field distributions, and emerging research topics.
3. **Data Agility & Hybrid Ingestion**: Combining external open APIs for live bibliographic data with curated structured datasets for funding programs.

---

## Datasets Used & Integration Strategy

Due to data availability constraints in the open-source ecosystem, the platform utilizes a hybrid data strategy:

1. **OpenAlex API (External Real-time Data)**
   - **Usage**: Research Trend Analysis & Publication Intelligence.
   - Provides access to millions of scholarly works, citation metrics, author records, and venue metadata without API key restrictions.

2. **32 Curated Funding Opportunities Dataset**
   - **Usage**: Research Funding Module & Recommendation Engine.
   - **Rationale**: Currently, there is **no completely free public API** that provides a comprehensive, structured dataset of global research grants and funding calls. To overcome this limitation, a custom dataset of **32 representative funding opportunities** (covering NSF, NIH, Horizon Europe, SBIR, climate funds, AI grants, etc.) was manually curated, structured, and seeded into the database.

3. **Google Patents Integration (Foundational)**
   - Integrated lightweight patent query endpoints to support publication-patent domain cross-referencing.

---

##  Milestones 1 & 2

### Milestone 1: Platform Setup, Security & Profile Engine
- **Core Architecture**: Established a decoupled architecture using FastAPI (backend) and React + Vite (frontend).
- **Authentication & RBAC**: Secure JWT-based authentication supporting Role-Based Access Control (`researcher`, `startup_founder`, `admin`).
- **Research Profile Management**: Full profile lifecycle enabling users to configure research domains, keywords, publication histories, track records, and location preferences.
- **Database Schema**: Designed relational models for Users, Profiles, Publications, and Funding Opportunities using SQLAlchemy ORM.

### Milestone 2: Research Funding Discovery & Trend Analytics
- **Funding Discovery Module**:
  - Search, filter, and view detailed funding opportunities.
  - Built-in **Recommendation Engine** that ranks grants based on domain overlap, role eligibility, geographic constraints, and keyword relevancy.
- **Research Trend Analysis Dashboard**:
  - Interactive topic search powered by live OpenAlex API data.
  - **Visual Charts & Metrics**:
    - **Publication Growth over Time** (*Recharts Line Chart* showing publication volume over a 12-year window).
    - **Hotspot & Topic Distribution** (*Recharts Bar Chart* highlighting top sub-fields by volume).
    - **Emerging Topics Metrics**: Calculates growth rates of rising topics in recent years vs. baseline distributions.
    - **High-Impact Papers**: Curated lists of top-cited publications for the searched query.
- **Admin Management Panel**: Endpoint and UI allowing administrators to view users, inspect database statistics, and seed/create new funding entries.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React (Vite), React Router DOM, Recharts (Visualizations), Axios, Vanilla CSS (Design Tokens) |
| **Backend** | Python, FastAPI, SQLAlchemy ORM, Pydantic v2, HTTPX (Async HTTP Client), PyJWT, Passlib (Bcrypt) |
| **Database** | SQLite (Development) / PostgreSQL-ready SQLAlchemy Engine |
| **External APIs** | OpenAlex REST API, Google Patents XHR Service |

---

## ⚙️ Quick Start & Installation

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ & npm

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate | Linux/macOS: source venv/bin/activate
pip install -r requirements.txt

# Seed the 32 curated funding dataset
python -m scripts.seed_funding

# Start FastAPI server
uvicorn app.main:app --reload
```
*Backend runs on `http://localhost:8000` (Swagger docs available at `http://localhost:8000/docs`).*

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
*Frontend app runs on `http://localhost:5173`.*