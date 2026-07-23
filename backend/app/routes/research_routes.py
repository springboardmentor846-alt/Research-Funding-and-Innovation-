from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.schemas.research_schema import ResearchCreate
from app.services.research_service import create_research

from app.utils.auth_dependency import get_current_user
from app.utils.role_checker import role_required
from app.services.research_service import (
    create_research,
    get_all_research
)
from app.services.research_service import (
    create_research,
    get_all_research,
    get_research_by_id,
    update_research,
    delete_research
)
router = APIRouter(
    prefix="/research",
    tags=["Research"]
)

@router.post("/create")
def create_research_project(
    research: ResearchCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    role_required(
        ["Researcher", "University", "Admin"]
    )(current_user)

    project = create_research(
        db,
        research,
        current_user["id"]
    )

    return {
        "message": "Research Project Created",
        "project_id": project.id
    }
@router.get("/all")
def view_all_research(
    db: Session = Depends(get_db)
):
    projects = get_all_research(db)

    return projects
@router.get("/{project_id}")
def view_research(
    project_id: int,
    db: Session = Depends(get_db)
):
    project = get_research_by_id(
        db,
        project_id
    )

    if not project:
        return {
            "message": "Research Project Not Found"
        }

    return project
@router.put("/update/{project_id}")
def update_research_project(
    project_id: int,
    research: ResearchCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    role_required(
        ["Researcher", "University", "Admin"]
    )(current_user)

    project = update_research(
        db,
        project_id,
        research
    )

    if not project:
        return {
            "message": "Research Project Not Found"
        }

    return {
        "message": "Research Project Updated",
        "project_id": project.id
    }
@router.delete("/delete/{project_id}")
def delete_research_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    role_required(
        ["Researcher", "University", "Admin"]
    )(current_user)

    deleted = delete_research(
        db,
        project_id
    )

    if not deleted:
        return {
            "message": "Research Project Not Found"
        }

    return {
        "message": "Research Project Deleted Successfully"
    }