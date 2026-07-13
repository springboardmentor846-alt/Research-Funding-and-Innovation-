from fastapi import APIRouter
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db

router = APIRouter(tags=["System"])


@router.get("/health")
def health():

    return {

        "status": "Healthy",

        "application": "Research Funding Platform",

        "version": "1.0.0",

        "timestamp": datetime.now()

    }

@router.get("/version")
def version():

    return {

        "version": "1.0.0",

        "backend": "FastAPI",

        "database": "PostgreSQL"

    }

router = APIRouter(tags=["System"])


@router.get("/database")
def database_status(
    db: Session = Depends(get_db)
):

    db.execute(text("SELECT 1"))

    return {
        "database": "Connected"
    }
@router.get("/system/statistics")
def statistics():

    return {

        "Completed Modules": 12,

        "Authentication": "Completed",

        "Research": "Completed",

        "Funding": "Completed",

        "Proposal": "Completed",

        "Technology": "Completed",

        "Innovation": "Completed",

        "Commercialization": "Completed",

        "Dashboard": "Completed",

        "Notification": "Completed",

        "Reports": "Completed"

    }