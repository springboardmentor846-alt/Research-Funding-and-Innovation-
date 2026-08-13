# Research Funding & Innovation Intelligence Platform

An AI-powered platform that helps researchers, startups, and innovation managers discover funding opportunities, track research trends, analyze patent landscapes, and receive commercialization recommendations — all from a single dashboard.

## Overview

This platform combines four core intelligence layers:
- **Funding Discovery** — matches researchers to relevant grants based on domain and eligibility
- **Research Intelligence** — tracks publication trends and emerging research topics
- **Patent Analytics** — analyzes patent landscapes, competitors, and technology clusters
- **Innovation Scoring** — generates a weighted innovation score and commercialization recommendations

## Tech Stack

**Backend**
- Python, FastAPI
- PostgreSQL (via Docker) + SQLAlchemy ORM
- JWT authentication with refresh tokens
- Role-based access control (Researcher, Startup Founder, Innovation Manager, Admin)

**Frontend**
- React (Vite)
- Recharts for data visualization
- Axios for API communication

**External Data Sources**
- OpenAlex API — live research publication search
- Grants.gov API — live U.S. federal funding search
- Verified real USPTO patent records

## Architecture

```
Client (React / Swagger UI)
        |
        v
FastAPI Backend (Uvicorn)
        |
   +----+----+----------+
   v         v          v
 Auth      Profile    Funding
 Module    Module     Module
   |         |          |
   +----+----+----------+
        v
  PostgreSQL (Docker)
```

## Features

- User registration & login with JWT (access + refresh tokens)
- Role-based access control on protected routes
- Research profile management (domains, keywords, publications, patents)
- Funding recommendation engine with domain + eligibility matching
- Live search of real U.S. federal grants (Grants.gov)
- Live import of real published research papers (OpenAlex)
- Publication trend analysis and emerging topic detection
- Patent landscape analysis, competitor analysis, and technology clustering
- Innovation scoring engine with weighted formula
- Commercialization recommendations
- Notifications and PDF/Excel report export
- API versioning (`/api/v1/`)
- Request-ID tracing middleware for request logging

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+
- Docker Desktop

### Backend Setup

```
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a `.env` file in the `backend` folder (see `.env.example`).

Start PostgreSQL:

```
cd infra
docker compose up -d
```

Run the backend:

```
cd backend
uvicorn app.main:app --reload
```

Backend runs at `http://127.0.0.1:8000` — interactive API docs at `http://127.0.0.1:8000/docs`.

### Frontend Setup

```
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`.

## API Overview

All endpoints are versioned under `/api/v1/`.

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/auth/register` | POST | Create a new account |
| `/api/v1/auth/login` | POST | Login, returns access + refresh tokens |
| `/api/v1/auth/refresh` | POST | Get a new access token |
| `/api/v1/auth/me` | GET | Get current user info |
| `/api/v1/profile/` | GET/POST | Manage research profile |
| `/api/v1/profile/publications` | GET/POST | Manage publications |
| `/api/v1/profile/patents` | GET/POST | Manage patents |
| `/api/v1/funding/` | GET/POST | List / add funding opportunities |
| `/api/v1/funding/recommended` | GET | Get personalized funding matches |

Full interactive documentation available at `/docs` when the server is running.

## Project Status

This project is being built in milestones as part of a mentorship program:

- Milestone 1 — Authentication, role-based access, research profiles (Complete)
- Milestone 2 — Funding discovery, research intelligence, trend analysis (Complete)
- Milestone 3 — Patent analytics, technology intelligence, innovation scoring (Complete)
- Milestone 4 — Testing, CI/CD, deployment (In Progress)

## Author

Upendra