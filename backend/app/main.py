from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import auth
from app.routers import profile
from app.routers import publication
from app.routers import patents
from app.routers import dashboard
from app.routers import funding
from app.routers import analytics


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Research Funding Platform",
    version="1.0"
)

# -------------------- CORS --------------------

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- Routers --------------------

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(publication.router)
app.include_router(patents.router)
app.include_router(dashboard.router)
app.include_router(funding.router)
app.include_router(analytics.router)

@app.get("/")
def home():
    return {
        "message": "Research Funding Platform API Running"
    }