from sqlalchemy.orm import Session

from app.models.research_profile import ResearchProfile
from app.models.funding import FundingOpportunity


class FundingAIService:

    def recommend(self, db: Session, profile_id: int):

        profile = db.query(ResearchProfile).filter(
            ResearchProfile.id == profile_id
        ).first()

        if not profile:
            return []

        opportunities = db.query(FundingOpportunity).all()

        recommendations = []

        for funding in opportunities:

            score = 0

            # Research Domain Match
            if (
                funding.research_domain
                and profile.research_domain
                and funding.research_domain.lower()
                == profile.research_domain.lower()
            ):
                score += 50

            # Publications
            score += min(profile.publications or 0, 20)

            # Patents
            score += (profile.patents or 0) * 5

            # Experience
            score += min(profile.experience or 0, 20)

            # Funding Amount Bonus
            if funding.funding_amount:

                if funding.funding_amount >= 1000000:
                    score += 20

                elif funding.funding_amount >= 500000:
                    score += 10

            recommendations.append({

                "funding_id": funding.id,

                "title": funding.title,

                "agency": funding.funding_agency,

                "research_domain": funding.research_domain,

                "source_type": funding.source_type,

                "funding_amount": funding.funding_amount,

                "deadline": funding.deadline,

                "eligibility": funding.eligibility,

                "recommendation_score": score

            })

        recommendations.sort(
            key=lambda x: x["recommendation_score"],
            reverse=True
        )

        return recommendations[:10]