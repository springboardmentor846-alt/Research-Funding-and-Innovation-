import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.middleware import RequestIDMiddleware
from app.core.limiter import limiter
from app.db.database import engine, Base
from app.models import user, password_reset_token, collaboration_request, startup
from app.api.auth import routes as auth_routes
from app.api.profile import routes as profile_routes
from app.api.funding import routes as funding_routes
from app.api.admin import routes as admin_routes
from app.api.collaboration import routes as collaboration_routes
from app.api.chatbot import routes as chatbot_routes
from app.api.startup import routes as startup_routes

app = FastAPI(title="Research Funding & Innovation Intelligence Platform")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(RequestIDMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(
    auth_routes.router,
    prefix="/api/v1/auth",
    tags=["Auth"]
)
app.include_router(
    profile_routes.router,
    prefix="/api/v1/profile",
    tags=["Profile"]
)
app.include_router(
    funding_routes.router,
    prefix="/api/v1/funding",
    tags=["Funding"]
)
app.include_router(
    admin_routes.router,
    prefix="/api/v1/admin",
    tags=["Admin"]
)
app.include_router(
    collaboration_routes.router,
    prefix="/api/v1/collaboration",
    tags=["Collaboration"]
)
app.include_router(
    chatbot_routes.router,
    prefix="/api/v1/chatbot",
    tags=["Chatbot"]
)
app.include_router(
    startup_routes.router,
    prefix="/api/v1/startup",
    tags=["Startup"]
)

UPLOAD_ROOT = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOAD_ROOT, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_ROOT), name="uploads")


@app.get("/")
def root():
    return {"message": "Research Funding & Innovation Intelligence Platform API is running"}