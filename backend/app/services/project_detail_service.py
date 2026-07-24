from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.project_detail import ProjectDetail
from app.models.innovation_portfolio import InnovationPortfolio
from app.schemas.project_detail_schema import (
    ProjectDetailCreate,
    ProjectDetailUpdate,
)
def create_project_detail(
    db: Session,
    portfolio_id: int,
    project_data: ProjectDetailCreate,
    user_id: int,
):
    # Check whether portfolio exists and belongs to the user
    portfolio = (
        db.query(InnovationPortfolio)
        .filter(
            InnovationPortfolio.id == portfolio_id,
            InnovationPortfolio.user_id == user_id,
        )
        .first()
    )

    if not portfolio:
        raise HTTPException(
            status_code=404,
            detail="Portfolio not found."
        )

    # Check if project detail already exists
    existing = (
        db.query(ProjectDetail)
        .filter(ProjectDetail.portfolio_id == portfolio_id)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Project details already exist."
        )

    project = ProjectDetail(
        portfolio_id=portfolio_id,
        github_url=str(project_data.github_url)
        if project_data.github_url else None,
        demo_url=str(project_data.demo_url)
        if project_data.demo_url else None,
        technology_stack=project_data.technology_stack,
        team_size=project_data.team_size,
        project_duration=project_data.project_duration,
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project
def get_project_detail(
    db: Session,
    portfolio_id: int,
):
    project = (
        db.query(ProjectDetail)
        .filter(ProjectDetail.portfolio_id == portfolio_id)
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project details not found."
        )

    return project
def update_project_detail(
    db: Session,
    portfolio_id: int,
    project_data: ProjectDetailUpdate,
):
    project = (
        db.query(ProjectDetail)
        .filter(ProjectDetail.portfolio_id == portfolio_id)
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project details not found."
        )

    update_data = project_data.model_dump(exclude_unset=True)

    if "github_url" in update_data and update_data["github_url"]:
        update_data["github_url"] = str(update_data["github_url"])

    if "demo_url" in update_data and update_data["demo_url"]:
        update_data["demo_url"] = str(update_data["demo_url"])

    for key, value in update_data.items():
        setattr(project, key, value)

    db.commit()
    db.refresh(project)

    return project
def delete_project_detail(
    db: Session,
    portfolio_id: int,
):
    project = (
        db.query(ProjectDetail)
        .filter(ProjectDetail.portfolio_id == portfolio_id)
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project details not found."
        )

    db.delete(project)
    db.commit()

    return {
        "message": "Project details deleted successfully."
    }