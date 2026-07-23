from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.schemas.innovation_portfolio_schema import (
    InnovationPortfolioCreate,
    InnovationPortfolioUpdate,
    InnovationPortfolioResponse,
)
from app.services.innovation_portfolio_service import (
    InnovationPortfolioService,
)

from app.utils.auth_dependency import get_current_user

router = APIRouter(
    prefix="/portfolio",
    tags=["Innovation Portfolio"],
)
@router.post(
    "/create",
    response_model=InnovationPortfolioResponse,
)
def create_portfolio(
    portfolio: InnovationPortfolioCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return InnovationPortfolioService.create_portfolio(
        db,
        portfolio,
        current_user,
    )


@router.get(
    "/my",
    response_model=List[InnovationPortfolioResponse],
)
def get_my_portfolios(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return InnovationPortfolioService.get_my_portfolios(
        db,
        current_user,
    )


@router.get(
    "/all",
    response_model=List[InnovationPortfolioResponse],
)
def get_all_portfolios(
    db: Session = Depends(get_db),
):
    return InnovationPortfolioService.get_all_portfolios(db)


@router.get(
    "/{portfolio_id}",
    response_model=InnovationPortfolioResponse,
)
def get_portfolio(
    portfolio_id: int,
    db: Session = Depends(get_db),
):
    return InnovationPortfolioService.get_portfolio_by_id(
        db,
        portfolio_id,
    )


@router.put(
    "/update/{portfolio_id}",
    response_model=InnovationPortfolioResponse,
)
def update_portfolio(
    portfolio_id: int,
    portfolio: InnovationPortfolioUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return InnovationPortfolioService.update_portfolio(
        db,
        portfolio_id,
        portfolio,
        current_user,
    )


@router.delete("/delete/{portfolio_id}")
def delete_portfolio(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return InnovationPortfolioService.delete_portfolio(
        db,
        portfolio_id,
        current_user,
    )