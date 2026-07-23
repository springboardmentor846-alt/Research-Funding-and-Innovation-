# Research Funding & Innovation Intelligence Platform

## Run the demo

Start the FastAPI API from the `backend` folder:

```powershell
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Start the React app from the `frontend` folder in another terminal:

```powershell
npm install
npm run dev
```

Open `http://localhost:5173`, register a researcher account, create a profile, then add publications, patents, and funding opportunities. The application uses a local SQLite database (`research_platform.db`) by default, so no PostgreSQL setup is required. Set `DATABASE_URL` to use a deployed database.

## Included Milestone 2 functionality

- Profile, publication, patent, and funding-opportunity CRUD
- Personalized dashboard with publication and portfolio charts
- Rule-based funding recommendations and transparent grant-match scoring
- Authenticated, responsive React interface backed by FastAPI
