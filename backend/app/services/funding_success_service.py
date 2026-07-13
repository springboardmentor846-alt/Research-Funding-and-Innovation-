from sqlalchemy.orm import Session

from app.models.funding import FundingOpportunity


class FundingSuccessService:

    def analyze(self, db: Session):

        opportunities = db.query(
            FundingOpportunity
        ).all()

        results = []

        for funding in opportunities:

            amount = funding.funding_amount or 0

            score = round(

                amount * 0.001 +

                (20 if funding.source_type else 0) +

                (15 if funding.eligibility else 0) +

                (10 if funding.description else 0),

                2

            )

            results.append({

                "funding_id": funding.id,

                "title": funding.title,

                "agency": funding.funding_agency,

                "research_domain": funding.research_domain,

                "funding_amount": amount,

                "source_type": funding.source_type,

                "success_score": score

            })

        results.sort(

            key=lambda x:
            x["success_score"],

            reverse=True

        )

        return results