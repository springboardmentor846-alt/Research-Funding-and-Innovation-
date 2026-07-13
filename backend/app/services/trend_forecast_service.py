from sqlalchemy.orm import Session

from app.models.research_paper import ResearchPaper


class TrendForecastService:

    def forecast(self, db: Session):

        papers = db.query(ResearchPaper).all()

        domains = {}

        for paper in papers:

            domain = paper.research_domain or "Unknown"

            if domain not in domains:

                domains[domain] = {
                    "papers": 0,
                    "citations": 0,
                    "trl": 0
                }

            domains[domain]["papers"] += 1

            domains[domain]["citations"] += (
                paper.citation_count or 0
            )

            domains[domain]["trl"] += (
                paper.trl_level or 1
            )

        results = []

        for domain, value in domains.items():

            avg_citations = (
                value["citations"] / value["papers"]
            )

            avg_trl = (
                value["trl"] / value["papers"]
            )

            score = (
                value["papers"] * 10 +
                avg_citations * 0.15 +
                avg_trl * 15
            )

            if score >= 250:
                prediction = "Emerging"

            elif score >= 120:
                prediction = "Growing"

            else:
                prediction = "Mature"

            results.append({

                "research_domain": domain,

                "papers": value["papers"],

                "average_citations": round(
                    avg_citations,
                    2
                ),

                "average_trl": round(
                    avg_trl,
                    2
                ),

                "trend_score": round(
                    score,
                    2
                ),

                "prediction": prediction

            })

        results.sort(
            key=lambda x: x["trend_score"],
            reverse=True
        )

        return results