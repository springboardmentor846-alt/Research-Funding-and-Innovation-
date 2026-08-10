# Research Funding & Innovation Intelligence Platform

An AI-powered full-stack platform that helps **researchers, startups, universities, and innovation teams** discover funding opportunities, analyze research trends, explore patents, and identify innovation opportunities.

## Project Overview

The platform combines **funding discovery, research intelligence, patent analytics, and innovation scoring** into a centralized system.

### Core Approach

1. **Research Profile Matching** – Matches user research interests, domains, and keywords with relevant funding opportunities.
2. **Research Trend Analysis** – Analyzes publication data to identify research trends and emerging topics.
3. **Patent & Innovation Intelligence** – Analyzes patent information and evaluates technology and innovation potential.

## Milestones Completed

### Milestone 1 — Core Setup & Authentication

* Set up FastAPI backend and React frontend.
* Implemented JWT authentication and role-based access.
* Created research profile management.
* Designed database models and core application structure.
* Integrated initial research and patent data sources.

### Milestone 2 — Funding & Research Intelligence

* Implemented funding opportunity discovery.
* Developed funding recommendation and grant matching.
* Added research trend and publication analysis.
* Created research and funding dashboards.
* Integrated research data for trend analysis.

### Milestone 3 — Patent & Innovation Intelligence

* Implemented patent landscape analysis.
* Added technology intelligence workflows.
* Developed innovation scoring.
* Added commercialization recommendations.
* Created innovation analytics dashboards.

The project plan defines Milestones 1–3 around core setup, funding/research intelligence, and patent/innovation intelligence respectively.

## Technology Stack

| Layer              | Technologies                         |
| ------------------ | ------------------------------------ |
| **Frontend**       | React, Vite, Tailwind CSS            |
| **Backend**        | Python, FastAPI                      |
| **Database**       | PostgreSQL, MongoDB                  |
| **Authentication** | JWT                                  |
| **AI/ML**          | Scikit-learn, XGBoost                |
| **Research Data**  | OpenAlex, CrossRef, Semantic Scholar |
| **Patent Data**    | Google Patents, The Lens, USPTO      |
| **Tools**          | Git, GitHub, Postman, Docker         |

## Quick Start

### Backend

```bash
cd backend

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```

Backend:

`http://127.0.0.1:8000`

Swagger:

`http://127.0.0.1:8000/docs`

### Frontend

Open another terminal:

```bash
cd frontend

npm install
npm run dev
```

Frontend:

`http://localhost:5173`

---
