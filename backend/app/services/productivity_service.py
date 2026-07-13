from sqlalchemy.orm import Session

from app.models.research_profile import ResearchProfile
from app.models.research_paper import ResearchPaper


class ProductivityService:

    def analyze(self, db: Session):

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

            total_output = (
                (profile.publications or 0) +
                (profile.patents or 0)
            )

            experience = profile.experience or 1

            productivity = round(
                total_output / experience,
                2
            )

            efficiency = round(
                citations / max(total_output, 1),
                2
            )

            score = round(
                productivity * 30 +
                efficiency * 0.25 +
                (profile.publications or 0) * 2 +
                (profile.patents or 0) * 5,
                2
            )

            results.append({
                "profile_id": profile.id,
                "organization": profile.organization,
                "research_domain": profile.research_domain,
                "publications": profile.publications,
                "patents": profile.patents,
                "experience": experience,
                "citations": citations,
                "productivity": productivity,
                "citation_efficiency": efficiency,
                "productivity_score": score
            })

        results.sort(
            key=lambda x: x["productivity_score"],
            reverse=True
        )

        return results