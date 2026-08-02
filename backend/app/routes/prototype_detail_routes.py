from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.utils.auth_dependency import get_current_user

from app.schemas.prototype_detail_schema import (
    PrototypeDetailCreate,
    PrototypeDetailUpdate,
    PrototypeDetailResponse,
)

from app.services.prototype_detail_service import (
    PrototypeDetailService,
)

router = APIRouter(
    prefix="/prototype-details",
    tags=["Prototype Details"]
)


@router.post(
    "/{portfolio_id}",
    response_model=PrototypeDetailResponse
)
def create_prototype_detail(
    portfolio_id: int,
    prototype: PrototypeDetailCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return PrototypeDetailService.create_prototype_detail(
        db,
        portfolio_id,
        prototype,
        current_user
    )


@router.get(
    "/{portfolio_id}",
    response_model=PrototypeDetailResponse
)
def get_prototype_detail(
    portfolio_id: int,
    db: Session = Depends(get_db)
):
    return PrototypeDetailService.get_prototype_detail(
        db,
        portfolio_id
    )


@router.put(
    "/{portfolio_id}",
    response_model=PrototypeDetailResponse
)
def update_prototype_detail(
    portfolio_id: int,
    prototype: PrototypeDetailUpdate,
    db: Session = Depends(get_db)
):
    return PrototypeDetailService.update_prototype_detail(
        db,
        portfolio_id,
        prototype
    )


@router.delete("/{portfolio_id}")
def delete_prototype_detail(
    portfolio_id: int,
    db: Session = Depends(get_db)
):
    return PrototypeDetailService.delete_prototype_detail(
        db,
        portfolio_id
    )