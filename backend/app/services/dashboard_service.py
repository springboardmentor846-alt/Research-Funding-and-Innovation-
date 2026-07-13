from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.research_paper import ResearchPaper
from app.models.funding import FundingOpportunity


class DashboardService:

    def overview(self, db: Session):

        total_papers = db.query(
            func.count(ResearchPaper.id)
        ).scalar()

        total_citations = db.query(
            func.sum(ResearchPaper.citation_count)
        ).scalar() or 0

        total_funding = db.query(
            func.count(FundingOpportunity.id)
        ).scalar()

        average_trl = db.query(
            func.avg(ResearchPaper.trl_level)
        ).scalar() or 0

        return {
            "total_papers": total_papers,
            "total_citations": total_citations,
            "total_funding": total_funding,
            "average_trl": round(float(average_trl), 2)
        }

    def publication_chart(self, db: Session):

        data = (
            db.query(
                ResearchPaper.publication_year,
                func.count(ResearchPaper.id)
            )
            .group_by(ResearchPaper.publication_year)
            .order_by(ResearchPaper.publication_year)
            .all()
        )

        return [
            {
                "year": row[0],
                "papers": row[1]
            }
            for row in data
        ]

    def citation_chart(self, db: Session):

        data = (
            db.query(
                ResearchPaper.publication_year,
                func.sum(ResearchPaper.citation_count)
            )
            .group_by(ResearchPaper.publication_year)
            .order_by(ResearchPaper.publication_year)
            .all()
        )

        return [
            {
                "year": row[0],
                "citations": int(row[1] or 0)
            }
            for row in data
        ]

    def trl_chart(self, db: Session):

        data = (
            db.query(
                ResearchPaper.trl_level,
                func.count(ResearchPaper.id)
            )
            .group_by(ResearchPaper.trl_level)
            .all()
        )

        return [
            {
                "trl_level": row[0],
                "papers": row[1]
            }
            for row in data
        ]

    def domain_chart(self, db: Session):

        data = (
            db.query(
                ResearchPaper.research_domain,
                func.count(ResearchPaper.id)
            )
            .group_by(ResearchPaper.research_domain)
            .all()
        )

        return [
            {
                "domain": row[0],
                "papers": row[1]
            }
            for row in data
        ]

    def funding_chart(self, db: Session):

        data = (
            db.query(
                FundingOpportunity.research_domain,
                func.count(FundingOpportunity.id)
            )
            .group_by(FundingOpportunity.research_domain)
            .all()
        )

        return [
            {
                "domain": row[0],
                "fundings": row[1]
            }
            for row in data
        ]
    
    def analytics(self, db: Session):

        return {

            "overview": self.overview(db),

            "publication_chart": self.publication_chart(db),

            "citation_chart": self.citation_chart(db),

            "trl_chart": self.trl_chart(db),

            "domain_chart": self.domain_chart(db),

            "funding_chart": self.funding_chart(db)

        }