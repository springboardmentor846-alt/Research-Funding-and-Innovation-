from sqlalchemy.orm import Session

from app.models.research_profile import ResearchProfile
from app.models.research_paper import ResearchPaper


class OrganizationRankingService:

    def rankings(self, db: Session):

        profiles = db.query(
            ResearchProfile
        ).all()

        organizations = {}

        for profile in profiles:

            org = profile.organization or "Unknown"

            if org not in organizations:

                organizations[org] = {

                    "researchers": 0,

                    "publications": 0,

                    "patents": 0,

                    "experience": 0,

                    "citations": 0,

                    "trl": 0,

                    "papers": 0

                }

            organizations[org]["researchers"] += 1

            organizations[org]["publications"] += (
                profile.publications or 0
            )

            organizations[org]["patents"] += (
                profile.patents or 0
            )

            organizations[org]["experience"] += (
                profile.experience or 0
            )

            papers = db.query(
                ResearchPaper
            ).filter(
                ResearchPaper.research_domain ==
                profile.research_domain
            ).all()

            organizations[org]["papers"] += len(
                papers
            )

            organizations[org]["citations"] += sum(
                paper.citation_count or 0
                for paper in papers
            )

            organizations[org]["trl"] += sum(
                paper.trl_level or 1
                for paper in papers
            )

        results = []

        for org, value in organizations.items():

            avg_trl = 0

            if value["papers"]:

                avg_trl = (
                    value["trl"] /
                    value["papers"]
                )

            score = (

                value["publications"] * 3 +

                value["patents"] * 5 +

                value["experience"] * 2 +

                value["citations"] * 0.02 +

                avg_trl * 20 +

                value["researchers"] * 10

            )

            results.append({

                "organization": org,

                "researchers": value["researchers"],

                "publications": value["publications"],

                "patents": value["patents"],

                "citations": value["citations"],

                "average_trl": round(
                    avg_trl,
                    2
                ),

                "organization_score": round(
                    score,
                    2
                )

            })

        results.sort(

            key=lambda x:
            x["organization_score"],

            reverse=True

        )

        return results