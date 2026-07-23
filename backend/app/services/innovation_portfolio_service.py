from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.innovation_portfolio import InnovationPortfolio
from app.schemas.innovation_portfolio_schema import (
    InnovationPortfolioCreate,
    InnovationPortfolioUpdate,
)


class InnovationPortfolioService:

    @staticmethod
    def create_portfolio(
        db: Session,
        portfolio: InnovationPortfolioCreate,
        current_user: dict,
    ):
        portfolio_data = portfolio.model_dump()

        # Convert HttpUrl fields to string
        for field in ["github_url", "paper_url", "prototype_link"]:
            if portfolio_data.get(field):
                portfolio_data[field] = str(portfolio_data[field])

        # Convert Enum values to string
        portfolio_data["category"] = portfolio.category.value
        portfolio_data["status"] = portfolio.status.value

        new_portfolio = InnovationPortfolio(
            user_id=current_user["id"],
            **portfolio_data
        )

        db.add(new_portfolio)
        db.commit()
        db.refresh(new_portfolio)

        return new_portfolio

    @staticmethod
    def get_my_portfolios(
        db: Session,
        current_user: dict,
    ):
        return (
            db.query(InnovationPortfolio)
            .filter(InnovationPortfolio.user_id == current_user["id"])
            .all()
        )

    @staticmethod
    def get_all_portfolios(db: Session):
        return db.query(InnovationPortfolio).all()

    @staticmethod
    def get_portfolio_by_id(
        db: Session,
        portfolio_id: int,
    ):
        portfolio = (
            db.query(InnovationPortfolio)
            .filter(InnovationPortfolio.id == portfolio_id)
            .first()
        )

        if not portfolio:
            raise HTTPException(
                status_code=404,
                detail="Portfolio not found",
            )

        return portfolio

    @staticmethod
    def update_portfolio(
        db: Session,
        portfolio_id: int,
        portfolio_data: InnovationPortfolioUpdate,
        current_user: dict,
    ):
        portfolio = (
            db.query(InnovationPortfolio)
            .filter(
                InnovationPortfolio.id == portfolio_id,
                InnovationPortfolio.user_id == current_user["id"],
            )
            .first()
        )

        if not portfolio:
            raise HTTPException(
                status_code=404,
                detail="Portfolio not found",
            )

        update_data = portfolio_data.model_dump(exclude_unset=True)

        # Convert HttpUrl fields to string
        for field in ["github_url", "paper_url", "prototype_link"]:
            if field in update_data and update_data[field]:
                update_data[field] = str(update_data[field])

        # Convert Enum values
        if "category" in update_data:
            update_data["category"] = update_data["category"].value

        if "status" in update_data:
            update_data["status"] = update_data["status"].value

        for key, value in update_data.items():
            setattr(portfolio, key, value)

        db.commit()
        db.refresh(portfolio)

        return portfolio

    @staticmethod
    def delete_portfolio(
        db: Session,
        portfolio_id: int,
        current_user: dict,
    ):
        portfolio = (
            db.query(InnovationPortfolio)
            .filter(
                InnovationPortfolio.id == portfolio_id,
                InnovationPortfolio.user_id == current_user["id"],
            )
            .first()
        )

        if not portfolio:
            raise HTTPException(
                status_code=404,
                detail="Portfolio not found",
            )

        db.delete(portfolio)
        db.commit()

        return {
            "message": "Innovation Portfolio deleted successfully."
        }