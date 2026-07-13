from sqlalchemy.orm import Session

from app.models.research_profile import ResearchProfile
from app.models.research_paper import ResearchPaper


class ResearchImpactService:

    def calculate(self, db: Session):

        profiles = db.query(ResearchProfile).all()

        results = []

        for profile in profiles:

            papers = db.query(ResearchPaper).filter(
                ResearchPaper.research_domain ==
                profile.research_domain
            ).all()

            citations = sum(
                paper.citation_count or 0
                for paper in papers
            )

            avg_trl = 0

            if papers:
                avg_trl = sum(
                    paper.trl_level or 1
                    for paper in papers
                ) / len(papers)

            impact_score = (
                min(profile.publications or 0, 50) * 3 +
                min(profile.patents or 0, 20) * 5 +
                min(profile.experience or 0, 30) * 2 +
                citations * 0.02 +
                avg_trl * 20
            )

            results.append({

                "profile_id": profile.id,

                "organization": profile.organization,

                "research_domain": profile.research_domain,

                "publications": profile.publications,

                "patents": profile.patents,

                "experience": profile.experience,

                "citations": citations,

                "average_trl": round(avg_trl, 2),

                "impact_score": round(impact_score, 2)

            })

        results.sort(
            key=lambda x: x["impact_score"],
            reverse=True
        )

        return results