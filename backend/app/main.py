from fastapi import FastAPI

from app.routes.auth_routes import router as auth_router
from app.routes.user_routes import router as user_router
from app.routes.research_routes import router as research_router
from app.routes.dashboard_routes import router as dashboard_router
from app.routes.user_profile_routes import router as user_profile_router
from app.routes.innovation_portfolio_routes import router as innovation_portfolio_router
app = FastAPI()

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(research_router)
app.include_router(
    dashboard_router
)
app.include_router(user_profile_router)
app.include_router(innovation_portfolio_router)
from app.models.innovation_portfolio import InnovationPortfolio
@app.get("/")
def home():
    return {
        "message": "Welcome to InnoBridge AI"
    }