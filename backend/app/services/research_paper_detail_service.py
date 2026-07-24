from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.innovation_portfolio import InnovationPortfolio
from app.models.research_paper_detail import ResearchPaperDetail
from app.schemas.research_paper_detail_schema import (
    ResearchPaperDetailCreate,
    ResearchPaperDetailUpdate,
)


class ResearchPaperDetailService:

    @staticmethod
    def create_research_paper_detail(
        db: Session,
        portfolio_id: int,
        research_paper: ResearchPaperDetailCreate,
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
            db.query(ResearchPaperDetail)
            .filter(
                ResearchPaperDetail.portfolio_id == portfolio_id
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Research paper details already exist."
            )

        new_research_paper = ResearchPaperDetail(
            portfolio_id=portfolio_id,
            paper_title=research_paper.paper_title,
            journal_name=research_paper.journal_name,
            publication_year=research_paper.publication_year,
            doi=research_paper.doi,
            paper_url=str(research_paper.paper_url)
            if research_paper.paper_url else None,
            authors=research_paper.authors,
            abstract=research_paper.abstract,
        )

        db.add(new_research_paper)
        db.commit()
        db.refresh(new_research_paper)

        return new_research_paper

    @staticmethod
    def get_research_paper_detail(
        db: Session,
        portfolio_id: int
    ):

        research_paper = (
            db.query(ResearchPaperDetail)
            .filter(
                ResearchPaperDetail.portfolio_id == portfolio_id
            )
            .first()
        )

        if not research_paper:
            raise HTTPException(
                status_code=404,
                detail="Research paper details not found."
            )

        return research_paper

    @staticmethod
    def update_research_paper_detail(
        db: Session,
        portfolio_id: int,
        research_paper: ResearchPaperDetailUpdate
    ):

        existing = (
            db.query(ResearchPaperDetail)
            .filter(
                ResearchPaperDetail.portfolio_id == portfolio_id
            )
            .first()
        )

        if not existing:
            raise HTTPException(
                status_code=404,
                detail="Research paper details not found."
            )

        update_data = research_paper.model_dump(exclude_unset=True)

        if "paper_url" in update_data and update_data["paper_url"]:
            update_data["paper_url"] = str(update_data["paper_url"])

        for key, value in update_data.items():
            setattr(existing, key, value)

        db.commit()
        db.refresh(existing)

        return existing

    @staticmethod
    def delete_research_paper_detail(
        db: Session,
        portfolio_id: int
    ):

        research_paper = (
            db.query(ResearchPaperDetail)
            .filter(
                ResearchPaperDetail.portfolio_id == portfolio_id
            )
            .first()
        )

        if not research_paper:
            raise HTTPException(
                status_code=404,
                detail="Research paper details not found."
            )

        db.delete(research_paper)
        db.commit()

        return {
            "message": "Research paper details deleted successfully."
        }