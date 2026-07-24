from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.utils.auth_dependency import get_current_user

from app.schemas.patent_detail_schema import (
    PatentDetailCreate,
    PatentDetailUpdate,
    PatentDetailResponse,
)

from app.services.patent_detail_service import (
    PatentDetailService,
)

router = APIRouter(
    prefix="/patent-details",
    tags=["Patent Details"]
)


@router.post(
    "/{portfolio_id}",
    response_model=PatentDetailResponse
)
def create_patent_detail(
    portfolio_id: int,
    patent: PatentDetailCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return PatentDetailService.create_patent_detail(
        db,
        portfolio_id,
        patent,
        current_user
    )


@router.get(
    "/{portfolio_id}",
    response_model=PatentDetailResponse
)
def get_patent_detail(
    portfolio_id: int,
    db: Session = Depends(get_db)
):
    return PatentDetailService.get_patent_detail(
        db,
        portfolio_id
    )


@router.put(
    "/{portfolio_id}",
    response_model=PatentDetailResponse
)
def update_patent_detail(
    portfolio_id: int,
    patent: PatentDetailUpdate,
    db: Session = Depends(get_db)
):
    return PatentDetailService.update_patent_detail(
        db,
        portfolio_id,
        patent
    )


@router.delete("/{portfolio_id}")
def delete_patent_detail(
    portfolio_id: int,
    db: Session = Depends(get_db)
):
    return PatentDetailService.delete_patent_detail(
        db,
        portfolio_id
    )