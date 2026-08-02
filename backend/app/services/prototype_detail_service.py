from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.innovation_portfolio import InnovationPortfolio
from app.models.prototype_detail import PrototypeDetail
from app.schemas.prototype_detail_schema import (
    PrototypeDetailCreate,
    PrototypeDetailUpdate,
)


class PrototypeDetailService:

    @staticmethod
    def create_prototype_detail(
        db: Session,
        portfolio_id: int,
        prototype: PrototypeDetailCreate,
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
            db.query(PrototypeDetail)
            .filter(
                PrototypeDetail.portfolio_id == portfolio_id
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Prototype details already exist."
            )

        new_prototype = PrototypeDetail(
            portfolio_id=portfolio_id,
            prototype_name=prototype.prototype_name,
            prototype_type=prototype.prototype_type,
            development_stage=prototype.development_stage,
            prototype_url=str(prototype.prototype_url)
            if prototype.prototype_url else None,
            demo_video_url=str(prototype.demo_video_url)
            if prototype.demo_video_url else None,
            description=prototype.description,
        )

        db.add(new_prototype)
        db.commit()
        db.refresh(new_prototype)

        return new_prototype

    @staticmethod
    def get_prototype_detail(
        db: Session,
        portfolio_id: int
    ):

        prototype = (
            db.query(PrototypeDetail)
            .filter(
                PrototypeDetail.portfolio_id == portfolio_id
            )
            .first()
        )

        if not prototype:
            raise HTTPException(
                status_code=404,
                detail="Prototype details not found."
            )

        return prototype

    @staticmethod
    def update_prototype_detail(
        db: Session,
        portfolio_id: int,
        prototype: PrototypeDetailUpdate
    ):

        existing = (
            db.query(PrototypeDetail)
            .filter(
                PrototypeDetail.portfolio_id == portfolio_id
            )
            .first()
        )

        if not existing:
            raise HTTPException(
                status_code=404,
                detail="Prototype details not found."
            )

        update_data = prototype.model_dump(exclude_unset=True)

        if "prototype_url" in update_data and update_data["prototype_url"]:
            update_data["prototype_url"] = str(update_data["prototype_url"])

        if "demo_video_url" in update_data and update_data["demo_video_url"]:
            update_data["demo_video_url"] = str(update_data["demo_video_url"])

        for key, value in update_data.items():
            setattr(existing, key, value)

        db.commit()
        db.refresh(existing)

        return existing

    @staticmethod
    def delete_prototype_detail(
        db: Session,
        portfolio_id: int
    ):

        prototype = (
            db.query(PrototypeDetail)
            .filter(
                PrototypeDetail.portfolio_id == portfolio_id
            )
            .first()
        )

        if not prototype:
            raise HTTPException(
                status_code=404,
                detail="Prototype details not found."
            )

        db.delete(prototype)
        db.commit()

        return {
            "message": "Prototype details deleted successfully."
        }