from fastapi import FastAPI
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app.routers.auth import router as auth_router
from app.routers import research_profile


from app.routers import funding
from app.routers import publication
from app.routers import patent
from app.routers import openalex
from app.routers import grant_prediction
from app.routers import orcid
from app.routers import crossref
from app.routers import dashboard
from app.routers import trends

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(research_profile.router)
app.include_router(funding.router)
app.include_router(publication.router)
app.include_router(patent.router)
app.include_router(openalex.router)
app.include_router(dashboard.router)
app.include_router(grant_prediction.router)
app.include_router(orcid.router)
app.include_router(crossref.router)
app.include_router(trends.router)

@app.get("/")
def home():
    return {"message": "Research Funding Platform Backend is running"}

@app.get("/db-test")
def test_database():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return {
            "message": "Database connection successful",
            "result": result.scalar()
        }