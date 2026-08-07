# Research Funding & Innovation Intelligence Platform (RFIP)

> **Phase 1 — Project Setup & Authentication**

A production-ready full-stack platform connecting researchers, startup founders, and innovation managers with funding intelligence, AI-powered matching, and collaboration tools.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Quick Start (Docker)](#quick-start-docker)
- [Local Development](#local-development)
  - [Backend](#backend-local-setup)
  - [Frontend](#frontend-local-setup)
- [Environment Variables](#environment-variables)
- [API Documentation](#api-documentation)
- [Authentication Flow](#authentication-flow)
- [Role-Based Access Control](#role-based-access-control)
- [Available Scripts](#available-scripts)
- [Phase 1 Features](#phase-1-features)
- [Roadmap](#roadmap)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                       Docker Network                         │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────────┐  │
│  │   PostgreSQL  │◄──│ FastAPI (API) │◄──│  React (SPA)  │  │
│  │   Port 5432  │    │  Port 8000   │    │   Port 80     │  │
│  └──────────────┘    └──────────────┘    └───────────────┘  │
│                            │                                  │
│                      JWT Auth + RBAC                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer      | Technology                                           |
|------------|------------------------------------------------------|
| Frontend   | React 18, Vite 6, Tailwind CSS 3, React Router 6, Axios |
| Backend    | FastAPI, SQLAlchemy 2 (async), Pydantic v2            |
| Auth       | JWT (access + refresh tokens), bcrypt, python-jose   |
| Database   | PostgreSQL 16, asyncpg                               |
| Container  | Docker, Docker Compose, Nginx                        |

---

## Project Structure

```
rfip/
├── docker-compose.yml          # Orchestrates all 3 services
├── .env.example                # Root environment template
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env.example
│   └── app/
│       ├── main.py             # FastAPI application factory
│       ├── api/
│       │   ├── dependencies/   # JWT auth deps, RBAC guards
│       │   └── v1/
│       │       ├── auth.py     # Auth endpoints
│       │       └── users.py    # User CRUD endpoints
│       ├── core/
│       │   ├── config.py       # Pydantic Settings
│       │   └── security.py     # JWT, bcrypt utilities
│       ├── database/
│       │   ├── session.py      # Async SQLAlchemy engine
│       │   └── init_db.py      # Table creation + seed
│       ├── middleware/         # Logging, security headers
│       ├── models/
│       │   └── user.py         # User + RefreshToken models
│       ├── schemas/
│       │   ├── user.py         # User Pydantic schemas
│       │   └── auth.py         # Auth request/response schemas
│       ├── services/
│       │   ├── auth_service.py # Auth business logic
│       │   └── user_service.py # User CRUD logic
│       └── utils/
│           └── email.py        # Email sending utilities
│
└── frontend/
    ├── Dockerfile
    ├── nginx.conf
    ├── .env.example
    ├── index.html
    ├── vite.config.js
    ├── tailwind.config.js
    ├── postcss.config.js
    └── src/
        ├── main.jsx            # React entry point
        ├── App.jsx             # Route definitions
        ├── index.css           # Global styles + Tailwind
        ├── context/
        │   └── AuthContext.jsx # Auth state + session hydration
        ├── services/
        │   ├── apiClient.js    # Axios + auto token refresh
        │   └── authService.js  # API wrappers
        ├── hooks/
        │   └── useRole.js      # RBAC hook
        ├── layouts/
        │   ├── AuthLayout.jsx  # Animated auth pages wrapper
        │   └── AppLayout.jsx   # Sidebar + topbar app shell
        ├── components/auth/
        │   ├── ProtectedRoute.jsx
        │   └── PublicRoute.jsx
        └── pages/
            ├── LandingPage.jsx
            ├── auth/
            │   ├── LoginPage.jsx
            │   ├── RegisterPage.jsx
            │   ├── ForgotPasswordPage.jsx
            │   ├── ResetPasswordPage.jsx
            │   └── VerifyEmailPage.jsx
            └── dashboard/
                ├── DashboardPage.jsx
                └── ProfilePage.jsx
```

---

## Prerequisites

| Tool        | Version  | Notes                         |
|-------------|----------|-------------------------------|
| Docker      | ≥ 24.x   | Required for Docker setup     |
| Docker Compose | ≥ 2.x | Comes with Docker Desktop     |
| Python      | ≥ 3.12   | For local backend dev         |
| Node.js     | ≥ 20.x   | For local frontend dev        |
| PostgreSQL  | ≥ 16     | For local DB (or use Docker)  |

---

## Quick Start (Docker)

### 1. Clone and configure environment

```bash
git clone <your-repo-url>
cd rfip

# Copy the environment template
cp .env.example .env
```

### 2. Edit `.env`

```env
# Generate a secure secret key:
# openssl rand -hex 64
SECRET_KEY=your_64_byte_hex_secret_here

POSTGRES_PASSWORD=your_strong_database_password
FIRST_SUPERUSER_PASSWORD=YourAdmin@Pass1!
```

### 3. Start all services

```bash
docker-compose up -d --build
```

### 4. Access the platform

| Service            | URL                                     |
|--------------------|-----------------------------------------|
| Frontend           | http://localhost                        |
| Backend API        | http://localhost:8000                   |
| Swagger UI         | http://localhost:8000/api/v1/docs       |
| ReDoc              | http://localhost:8000/api/v1/redoc      |

### Default admin credentials

```
Email:    admin@rfip.dev
Password: Admin@123!
```

> **⚠️ Change the default password immediately in production!**

---

## Local Development

### Backend Local Setup

```bash
cd rfip/backend

# Create and activate virtual environment
python -m venv .venv
# Windows:
.\.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your local PostgreSQL credentials

# Start the development server
uvicorn app.main:app --reload --port 8000
```

### Frontend Local Setup

```bash
cd rfip/frontend

# Install dependencies
npm install

# Copy environment
cp .env.example .env.local
# Edit VITE_API_URL if needed (default: /api/v1 proxied to :8000)

# Start development server
npm run dev
```

The Vite dev server runs at **http://localhost:5173** and proxies `/api/*` to `http://localhost:8000`.

---

## Environment Variables

### Root `.env` (Docker Compose)

| Variable                 | Required | Default         | Description                         |
|--------------------------|----------|-----------------|-------------------------------------|
| `SECRET_KEY`             | ✅        | —               | JWT signing key (64+ bytes hex)     |
| `POSTGRES_USER`          | ✅        | `rfip_user`     | Database username                   |
| `POSTGRES_PASSWORD`      | ✅        | —               | Database password                   |
| `POSTGRES_DB`            | ✅        | `rfip_db`       | Database name                       |
| `EMAILS_ENABLED`         | ❌        | `false`         | Enable SMTP email sending           |
| `SMTP_HOST`              | ❌        | —               | SMTP server host                    |
| `SMTP_USER`              | ❌        | —               | SMTP username                       |
| `SMTP_PASSWORD`          | ❌        | —               | SMTP password                       |
| `FRONTEND_URL`           | ❌        | `http://localhost` | Used in email reset links        |
| `FIRST_SUPERUSER_EMAIL`  | ❌        | `admin@rfip.dev` | Auto-created admin email           |
| `FIRST_SUPERUSER_PASSWORD`| ❌       | `Admin@123!`    | Auto-created admin password         |

---

## API Documentation

Interactive Swagger UI is available at: `http://localhost:8000/api/v1/docs`

### Authentication Endpoints

| Method | Endpoint                        | Auth    | Description                    |
|--------|---------------------------------|---------|--------------------------------|
| POST   | `/api/v1/auth/register`         | Public  | Create new user account        |
| POST   | `/api/v1/auth/login`            | Public  | Login and get token pair       |
| POST   | `/api/v1/auth/refresh`          | Public  | Rotate refresh token           |
| POST   | `/api/v1/auth/logout`           | Bearer  | Revoke refresh token           |
| POST   | `/api/v1/auth/forgot-password`  | Public  | Send password reset email      |
| POST   | `/api/v1/auth/reset-password`   | Public  | Reset password via token       |
| POST   | `/api/v1/auth/verify-email`     | Public  | Verify email address           |
| GET    | `/api/v1/auth/me`               | Bearer  | Get current user               |

### User Endpoints

| Method | Endpoint                  | Auth       | Description              |
|--------|---------------------------|------------|--------------------------|
| GET    | `/api/v1/users/me`        | Bearer     | Get my profile           |
| PATCH  | `/api/v1/users/me`        | Bearer     | Update my profile        |
| PUT    | `/api/v1/users/me/password`| Bearer    | Change my password       |
| GET    | `/api/v1/users/`          | Admin      | List all users           |
| GET    | `/api/v1/users/{id}`      | Admin      | Get user by ID           |
| PATCH  | `/api/v1/users/{id}`      | Admin      | Admin update user        |
| DELETE | `/api/v1/users/{id}`      | Admin      | Delete user              |

---

## Authentication Flow

```
Register ──► Verification Email ──► Verify Email
                                          │
Login ──────────────────────────────────► Access Token (30min)
                                          + Refresh Token (7 days)
                                          │
Access Protected Route ─────────────────► [Bearer Token]
                                          │
Token Expired ──────────────────────────► POST /auth/refresh
                                          (old token revoked → new pair issued)
                                          │
Logout ──────────────────────────────────► Token revoked in DB
```

---

## Role-Based Access Control

| Role                | Permissions                                              |
|---------------------|----------------------------------------------------------|
| `researcher`        | Own profile CRUD, dashboard access                       |
| `startup_founder`   | Own profile CRUD, dashboard access                       |
| `innovation_manager`| Own profile CRUD, dashboard access, limited admin views  |
| `administrator`     | Full platform access, user management                    |

**Frontend RBAC hook:**
```jsx
import { useRole } from '@/hooks/useRole'

function AdminPanel() {
  const isAdmin = useRole('administrator')
  if (!isAdmin) return <Navigate to="/dashboard" />
  return <AdminContent />
}
```

**Backend RBAC dependency:**
```python
from app.api.dependencies import require_admin, require_roles
from app.models.user import UserRole

@router.get("/admin-only", dependencies=[Depends(require_admin)])
async def admin_endpoint(): ...

@router.get("/managers", dependencies=[Depends(require_roles(UserRole.INNOVATION_MANAGER, UserRole.ADMINISTRATOR))])
async def manager_endpoint(): ...
```

---

## Available Scripts

### Docker

```bash
# Start all services (detached)
docker-compose up -d --build

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop all services
docker-compose down

# Stop and remove volumes (fresh DB)
docker-compose down -v

# Rebuild a single service
docker-compose up -d --build backend
```

### Backend

```bash
# Run with hot reload
uvicorn app.main:app --reload --port 8000

# Run tests (Phase 2)
pytest

# Format code
black app/
ruff check app/ --fix
```

### Frontend

```bash
npm run dev       # Start dev server
npm run build     # Build for production
npm run preview   # Preview production build
npm run lint      # Run ESLint
```

---

## Phase 1 Features

- ✅ Complete project structure (frontend + backend)
- ✅ PostgreSQL database with async SQLAlchemy
- ✅ SQLAlchemy models: `User`, `RefreshToken`
- ✅ JWT authentication (access + refresh tokens with rotation)
- ✅ Bcrypt password hashing
- ✅ Role-Based Access Control (4 roles)
- ✅ REST API: Register, Login, Logout, Refresh, Forgot/Reset Password, Verify Email
- ✅ User profile CRUD (self-service + admin)
- ✅ Admin user management endpoints
- ✅ React frontend with React Router v6
- ✅ Auth context with session rehydration
- ✅ Axios client with automatic token refresh (queue-based)
- ✅ Protected & public route guards
- ✅ Landing page with features, roles, and stats
- ✅ Login, Register (with password strength meter), Forgot/Reset Password, Verify Email pages
- ✅ Dashboard placeholder
- ✅ Profile page with tabbed UI (info + password change)
- ✅ Glassmorphism UI with animations and dark theme
- ✅ CORS, security headers middleware
- ✅ Swagger/ReDoc documentation
- ✅ Dockerized (PostgreSQL + FastAPI + React/Nginx)
- ✅ Docker Compose orchestration
- ✅ Environment variable management

---

## Roadmap

| Phase | Features                                                        |
|-------|-----------------------------------------------------------------|
| 1     | ✅ Auth, RBAC, User management (current)                         |
| 2     | Funding database, Grant discovery, Search & filters             |
| 3     | AI-powered funding recommendation engine                        |
| 4     | Patent analytics, citation networks, landscape visualisations   |
| 5     | Collaboration hub, messaging, project spaces                    |
| 6     | Innovation trend analytics, market intelligence dashboards      |

---

## License

MIT © RFIP Platform Team
