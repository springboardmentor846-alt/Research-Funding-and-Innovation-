from sqlalchemy.orm import Session
from app.models.research_paper import ResearchPaper


class OpportunityService:

    def discover(self, db: Session):

        papers = db.query(ResearchPaper).all()

        opportunities = []

        for paper in papers:

            score = (
                (paper.citation_count or 0) * 0.35 +
                (paper.github_stars or 0) * 0.25 +
                (paper.github_forks or 0) * 0.10+
                 ((paper.trl_level or 1) * 50) +
                 ((paper.github_watchers or 0) * 0.15)
            )

            opportunities.append({
                "paper_id": paper.id,
                "title": paper.title,
                "research_domain": paper.research_domain,
                "citation_count": paper.citation_count,
                "github_stars": paper.github_stars,
                "trl_level": paper.trl_level,
                "opportunity_score": round(score, 2)
            })

        opportunities.sort(
            key=lambda x: x["opportunity_score"],
            reverse=True
        )

        return opportunities