from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db import get_db

from app.schemas.project_detail_schema import (
    ProjectDetailCreate,
    ProjectDetailUpdate,
    ProjectDetailResponse,
)

from app.services.project_detail_service import (
    create_project_detail,
    get_project_detail,
    update_project_detail,
    delete_project_detail,
)

from app.utils.auth_dependency import get_current_user
router = APIRouter(
    prefix="/project-details",
    tags=["Project Details"]
)
@router.post(
    "/{portfolio_id}",
    response_model=ProjectDetailResponse
)
def create_project(
    portfolio_id: int,
    project_data: ProjectDetailCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return create_project_detail(
        db,
        portfolio_id,
        project_data,
        current_user["id"],
    )
@router.get(
    "/{portfolio_id}",
    response_model=ProjectDetailResponse
)
def get_project(
    portfolio_id: int,
    db: Session = Depends(get_db),
):
    return get_project_detail(
        db,
        portfolio_id,
    )
@router.put(
    "/{portfolio_id}",
    response_model=ProjectDetailResponse
)
def update_project(
    portfolio_id: int,
    project_data: ProjectDetailUpdate,
    db: Session = Depends(get_db),
):
    return update_project_detail(
        db,
        portfolio_id,
        project_data,
    )
@router.delete("/{portfolio_id}")
def delete_project(
    portfolio_id: int,
    db: Session = Depends(get_db),
):
    return delete_project_detail(
        db,
        portfolio_id,
    )