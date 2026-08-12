from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import engine, Base
from app.models import user
from app.api.auth import routes as auth_routes
from app.api.profile import routes as profile_routes
from app.api.funding import routes as funding_routes
from app.api.admin import routes as admin_routes

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Research Funding & Innovation Intelligence Platform"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    auth_routes.router,
    prefix="/api/auth",
    tags=["Auth"]
)
app.include_router(
    profile_routes.router,
    prefix="/api/profile",
    tags=["Profile"]
)
app.include_router(
    funding_routes.router,
    prefix="/api/funding",
    tags=["Funding"]
)
app.include_router(
    admin_routes.router,
    prefix="/api/admin",
    tags=["Admin"]
)


@app.get("/")
def home():
    return {
        "message": "Platform Running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }