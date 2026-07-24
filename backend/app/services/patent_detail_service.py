from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.innovation_portfolio import InnovationPortfolio
from app.models.patent_detail import PatentDetail
from app.schemas.patent_detail_schema import (
    PatentDetailCreate,
    PatentDetailUpdate,
)


class PatentDetailService:

    @staticmethod
    def create_patent_detail(
        db: Session,
        portfolio_id: int,
        patent: PatentDetailCreate,
        current_user: dict
    ):

        portfolio = (
            db.query(InnovationPortfolio)
            .filter(
                InnovationPortfolio.id == portfolio_id,
                InnovationPortfolio.user_id == current_user["id"]
            )
            .first()
        )

        if not portfolio:
            raise HTTPException(
                status_code=404,
                detail="Innovation Portfolio not found."
            )

        existing = (
            db.query(PatentDetail)
            .filter(
                PatentDetail.portfolio_id == portfolio_id
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Patent details already exist."
            )

        new_patent = PatentDetail(
            portfolio_id=portfolio_id,
            patent_title=patent.patent_title,
            patent_number=patent.patent_number,
            patent_status=patent.patent_status,
            filing_date=patent.filing_date,
            publication_date=patent.publication_date,
            inventors=patent.inventors,
            patent_url=str(patent.patent_url)
            if patent.patent_url else None,
            description=patent.description,
        )

        db.add(new_patent)
        db.commit()
        db.refresh(new_patent)

        return new_patent

    @staticmethod
    def get_patent_detail(
        db: Session,
        portfolio_id: int
    ):

        patent = (
            db.query(PatentDetail)
            .filter(
                PatentDetail.portfolio_id == portfolio_id
            )
            .first()
        )

        if not patent:
            raise HTTPException(
                status_code=404,
                detail="Patent details not found."
            )

        return patent

    @staticmethod
    def update_patent_detail(
        db: Session,
        portfolio_id: int,
        patent: PatentDetailUpdate
    ):

        existing = (
            db.query(PatentDetail)
            .filter(
                PatentDetail.portfolio_id == portfolio_id
            )
            .first()
        )

        if not existing:
            raise HTTPException(
                status_code=404,
                detail="Patent details not found."
            )

        update_data = patent.model_dump(exclude_unset=True)

        if "patent_url" in update_data and update_data["patent_url"]:
            update_data["patent_url"] = str(update_data["patent_url"])

        for key, value in update_data.items():
            setattr(existing, key, value)

        db.commit()
        db.refresh(existing)

        return existing

    @staticmethod
    def delete_patent_detail(
        db: Session,
        portfolio_id: int
    ):

        patent = (
            db.query(PatentDetail)
            .filter(
                PatentDetail.portfolio_id == portfolio_id
            )
            .first()
        )

        if not patent:
            raise HTTPException(
                status_code=404,
                detail="Patent details not found."
            )

        db.delete(patent)
        db.commit()

        return {
            "message": "Patent details deleted successfully."
        }