# Research Funding & Innovation Intelligence Platform

Enterprise Monorepo Architecture for AI-powered Research Funding Discovery, Patent Analytics, Technology Intelligence, and Innovation Commercialization.

## Monorepo Architecture Overview

```
.
├── backend/            # FastAPI Core Monolith Backend (Clean Architecture)
├── frontend/           # React + Vite + TypeScript Single Page Application
├── ai-services/        # Python AI, NLP, BERTopic, & RAG Pipeline Workers
├── shared/             # Shared Schemas, OpenAPI Specs, & TypeScript Contracts
├── infrastructure/     # Dockerfiles, Compose specs, Helm Charts, & Terraform
├── docs/               # Architecture Specs, SRS Documents, API Runbooks
├── scripts/            # Database Seeds, Migration Utilities, ETL Ingestion
└── tests/              # End-to-End System & Integration Suite
```

## Getting Started

Refer to individual README files within `backend/`, `frontend/`, and `ai-services/` for localized setup and development instructions.
