from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.research_paper import ResearchPaper


class CompetitiveService:

    def domain_statistics(self, db: Session):

        results = (
            db.query(
                ResearchPaper.research_domain,
                func.count(ResearchPaper.id),
                func.avg(ResearchPaper.citation_count),
                func.avg(ResearchPaper.github_stars)
            )
            .group_by(ResearchPaper.research_domain)
            .all()
        )

        domains = []

        for item in results:

            avg_citations = float(item[2] or 0)
            avg_github_stars = float(item[3] or 0)

            competition_score = (
            avg_citations * 0.40 +
            avg_github_stars * 0.35 +
            item[1] * 25
            )

            domains.append({

                "research_domain": item[0],

                "papers": item[1],

                "average_citations": round(avg_citations, 2),

                "average_github_stars": round(avg_github_stars, 2),

               

                "competition_score": round(
                    competition_score,
                    2
                )

            })

        domains.sort(

            key=lambda x: x["competition_score"],

            reverse=True

        )

        return domains