# Research Funding & Innovation Intelligence Platform

A full-stack web platform designed to support researchers in discovering funding opportunities, managing research outputs, exploring patent landscapes, analyzing research trends, and receiving personalized research intelligence.

The platform combines researcher profile information with external scholarly and patent data, semantic recommendation techniques, and machine learning to provide personalized insights for research and funding discovery.

---

## Project Overview

Researchers often need to use multiple independent platforms for funding discovery, publication management, patent analysis, and research intelligence.

The **Research Funding & Innovation Intelligence Platform** brings these workflows together into a single system.

The platform allows researchers to:

- Create and manage a structured research profile
- Maintain research domains, keywords, and technology areas
- Manage publications and patents
- Import scholarly information from external research sources
- Discover funding opportunities
- Receive personalized funding recommendations
- Check funding eligibility
- Estimate grant success probability using machine learning
- Discover relevant patents
- Analyze global patent landscapes
- Explore research trends

---

## Core Features

### 1. Authentication and Role-Based Access

The platform provides authenticated access to protected research functionality.

Features include:

- User registration and login
- JWT-based authentication
- Protected frontend routes
- Backend authorization
- Researcher role-based access control

---

### 2. Research Profile Management

Researchers can build a structured profile containing information used throughout the platform for personalization.

Profile-related modules include:

- Research profile
- Research domains
- Research keywords
- Technology areas
- Organization information
- Publications
- Patents

Research domains, keywords, technology areas, and other profile information are also used by the recommendation system to understand the researcher's interests.

---

### 3. Publication Management

Researchers can maintain their scholarly outputs within the platform.

Supported functionality includes:

- Add publications
- View publications
- Update publication information
- Delete publications
- Import researcher publications through ORCID integration

Publication metadata may include:

- Title
- Authors
- Publication type
- Journal or conference
- Publisher
- Publication date
- DOI
- URL
- Abstract
- Citation information

---

### 4. Research Library and OpenAlex Integration

The platform integrates with OpenAlex for scholarly research discovery.

Researchers can search for publications using a research topic or keyword and control the number of publications retrieved.

Example:

```text
Topic: Artificial Intelligence in Healthcare
Number of Publications: 10
```

The system retrieves relevant scholarly works and can maintain them separately from the researcher's own publications.

This creates a clear distinction between:

- **My Publications** — work authored by the researcher
- **Research Library** — external scholarly work collected for research and reference

---

### 5. Personalized Funding Recommendations

Funding opportunities are ranked according to their relevance to the researcher's profile.

The recommendation process considers information such as:

- Research domains
- Research keywords
- Technology areas
- Funding research domain
- Grant description
- Funding keywords

A semantic recommendation engine constructs a representation of the researcher and compares it with available funding opportunities.

The general workflow is:

```text
Research Profile
      ↓
Domains + Keywords + Technology Areas
      ↓
Researcher Representation
      ↓
Funding Opportunity Data
      ↓
Semantic Similarity
      ↓
Relevance Score
      ↓
Ranked Funding Recommendations
```

The resulting match score represents **research relevance**, not grant success probability.

---

### 6. Funding Eligibility

Funding opportunities contain eligibility-related information such as:

- Eligible countries
- International applicant eligibility
- Qualification requirements
- Career stage
- Experience requirements
- Funding status

This information can be used along with research relevance to identify opportunities suitable for a researcher.

---

### 7. Grant Success Prediction

The platform contains a machine-learning-based grant prediction module.

A trained model is loaded by the backend and used to estimate grant success probability from relevant input features.

```text
Grant / Researcher Features
        ↓
ML Prediction Service
        ↓
Trained Model
        ↓
Probability Prediction
        ↓
Grant Success %
```

This is separate from funding recommendation:

- **Funding Recommendation:** How relevant is this opportunity to the researcher?
- **Grant Prediction:** What is the estimated probability of grant success?

---

### 8. Patent Management and Intelligence

The platform supports patent-related workflows including researcher patent management and patent intelligence.

Researchers can:

- Maintain patent information
- Discover relevant patent information
- Explore patent activity related to a technology

---

### 9. Global Patent Landscape

Researchers can enter a technology or keyword to analyze patent activity related to that topic.

Example:

```text
Machine Learning
Computer Vision
Renewable Energy
Battery Technology
```

The backend retrieves patent information using the Lens integration and performs aggregation to generate patent intelligence.

The Patent Landscape includes information such as:

- Total patents analyzed
- Country/jurisdiction distribution
- Leading applicants and organizations
- Technology/CPC classifications
- Filing trends
- Patent status information
- Generated summary insights

Workflow:

```text
Technology / Keyword
        ↓
Patent Landscape API
        ↓
Lens Service
        ↓
Patent Data
        ↓
Aggregation and Analysis
        ↓
Patent Intelligence Dashboard
```

---

### 10. Research Trends

The Research Trends module provides analytics related to research activity in selected areas.

It uses scholarly research data and backend processing to help researchers understand developments and activity within a research field.

---

## External Research Integrations

The project uses external research information sources for different purposes.

| Source | Purpose |
|---|---|
| OpenAlex | Scholarly publication discovery and research metadata |
| ORCID | Researcher identity and researcher publication import |
| Lens | Patent search and patent intelligence |
| Crossref | Scholarly publication and DOI metadata |

---

## Technology Stack

### Frontend

- React
- Vite
- JavaScript
- HTML
- CSS
- Bootstrap
- Axios

### Backend

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- Uvicorn
- Alembic

### Database

- PostgreSQL

### AI / Machine Learning

- Scikit-learn
- Joblib
- Semantic similarity and recommendation logic
- ML-based grant probability prediction

### External APIs / Data Sources

- OpenAlex
- ORCID
- Lens
- Crossref

### Development Tools

- Git
- GitHub
- Visual Studio Code
- pgAdmin

---

## Project Architecture

```text
Research-Funding-Innovation-Platform/
│
├── backend/
│   └── app/
│       ├── ai/
│       ├── core/
│       ├── ml/
│       ├── models/
│       ├── routers/
│       ├── schemas/
│       ├── services/
│       ├── config.py
│       ├── database.py
│       ├── dependencies.py
│       └── main.py
│
├── frontend/
│   ├── public/
│   └── src/
│       ├── api/
│       ├── assets/
│       ├── components/
│       ├── pages/
│       ├── App.jsx
│       ├── App.css
│       └── main.jsx
│
├── docs/
│
├── .gitignore
└── README.md
```

---

## Backend Architecture

The FastAPI backend follows a modular architecture.

### Models

`backend/app/models/`

SQLAlchemy models define PostgreSQL database tables such as:

- Users
- Research profiles
- Research domains
- Research keywords
- Technology areas
- Publications
- Patents
- Funding opportunities

### Routers

`backend/app/routers/`

Routers expose REST API endpoints and handle:

- Request validation
- Authentication
- Authorization
- Calling service-layer functionality
- Returning API responses

### Schemas

`backend/app/schemas/`

Pydantic schemas validate request and response data.

### Services

`backend/app/services/`

The service layer contains the primary application and integration logic.

Examples include:

```text
ai_service.py
crossref_service.py
dashboard_service.py
grant_prediction_service.py
lens_service.py
openalex_service.py
orcid_service.py
patent_landscape_service.py
trend_service.py
funding_collection_service.py
funding_source_service.py
funding_eligibility_service.py
```

This separation keeps API routing, database models, external integrations, and business logic independent.

---

## Frontend Architecture

### Pages

`frontend/src/pages/`

Contains major application screens such as:

- Dashboard
- Research Profile
- Research Domains
- Research Keywords
- Technology Areas
- Organization Information
- Publications
- Patents
- Funding Opportunities
- Grant Prediction
- Patent Landscape
- Research Trends

### API Layer

`frontend/src/api/`

Contains Axios-based functions responsible for communication between React and the FastAPI backend.

### Components

`frontend/src/components/`

Contains reusable application components including layouts and protected route components.

---

## Application Flow

The general application flow is:

```text
Researcher
    ↓
React Frontend
    ↓
Frontend API Layer
    ↓
FastAPI Router
    ↓
Authentication / Authorization
    ↓
Service Layer
    ↓
┌─────────────────────────────┐
│ PostgreSQL                  │
│ OpenAlex                    │
│ ORCID                       │
│ Lens                        │
│ Crossref                    │
│ AI / ML Services            │
└─────────────────────────────┘
    ↓
Processed / Personalized Data
    ↓
FastAPI Response
    ↓
React Dashboard
```

---

## Personalization Architecture

A central objective of the platform is to provide researcher-specific intelligence rather than displaying identical information to every user.

```text
Research Profile
      │
      ├── Domains
      ├── Keywords
      ├── Technology Areas
      ├── Publications
      └── Research Information
              ↓
      Researcher Representation
              ↓
      Recommendation / Analytics Layer
              ↓
 ┌────────────┼────────────┐
 ↓            ↓            ↓
Funding     Patents     Publications
```

This allows research information from different sources to be transformed into more useful, personalized results.

---

## Running the Project Locally

### 1. Clone the Repository

```bash
git clone <repository-url>
cd research-funding-innovation-platform
```

### 2. Backend Setup

Navigate to the backend:

```bash
cd backend
```

Create and activate a virtual environment.

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure the required environment variables in the backend `.env` file.

Apply database migrations:

```bash
alembic upgrade head
```

Start FastAPI:

```bash
uvicorn app.main:app --reload
```

The backend will normally run at:

```text
http://127.0.0.1:8000
```

FastAPI documentation is available at:

```text
http://127.0.0.1:8000/docs
```

### 3. Frontend Setup

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Vite will normally start the frontend at:

```text
http://localhost:5173
```

---

## Database Migrations

Alembic is used for database schema migrations.

After modifying SQLAlchemy models:

```bash
alembic revision --autogenerate -m "migration description"
```

Apply the migration:

```bash
alembic upgrade head
```

---

## Security Notes

Sensitive configuration should never be committed to GitHub.

Do not commit:

```text
.env
API keys
database passwords
JWT secrets
access tokens
private credentials
```

These should be configured using environment variables.

---

## Current Development Status

Implemented functionality includes:

- Authentication and researcher access control
- Research profile management
- Research domains
- Research keywords
- Technology areas
- Organization information
- Publication management
- ORCID integration
- OpenAlex research discovery
- Patent management
- Funding opportunity management
- Personalized funding recommendation
- Funding eligibility logic
- ML-based grant success prediction
- Patent landscape analytics
- Research trend analytics
- External research data integrations

Further development can extend automated funding collection, alerting, advanced CPC interpretation, recommendation quality, and production deployment.

---

## Project Objective

The objective of this project is to demonstrate how research information from multiple sources can be integrated with researcher profiles, recommendation techniques, analytics, and machine learning to create a unified **Research Funding and Innovation Intelligence Platform**.