from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.research_paper import ResearchPaper


class ResearchGapService:

    def analyze(self, db: Session):

        domains = db.query(

            ResearchPaper.research_domain,

            func.count(ResearchPaper.id),

            func.sum(ResearchPaper.citation_count)

        ).group_by(

            ResearchPaper.research_domain

        ).all()

        results = []

        for domain in domains:

            research_domain = domain[0]

            papers = domain[1] or 0

            citations = int(domain[2] or 0)

            gap_score = round(

                (100 / max(papers, 1)) +

                (1000 / max(citations, 1))

            , 2)

            if gap_score > 50:

                level = "High"

            elif gap_score > 20:

                level = "Medium"

            else:

                level = "Low"

            results.append({

                "research_domain": research_domain,

                "papers": papers,

                "citations": citations,

                "gap_score": gap_score,

                "research_gap": level

            })

        results.sort(

            key=lambda x: x["gap_score"],

            reverse=True

        )

        return results