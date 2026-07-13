from sqlalchemy.orm import Session

from app.models.research_profile import ResearchProfile


class CollaborationNetworkService:

    def network(self, db: Session):

        profiles = db.query(ResearchProfile).all()

        collaborations = []

        for i in range(len(profiles)):

            for j in range(i + 1, len(profiles)):

                p1 = profiles[i]
                p2 = profiles[j]

                score = 0

                if (
                    p1.research_domain
                    and p2.research_domain
                    and p1.research_domain.lower()
                    == p2.research_domain.lower()
                ):
                    score += 50

                keywords1 = set(
                    (p1.keywords or "").lower().split(",")
                )

                keywords2 = set(
                    (p2.keywords or "").lower().split(",")
                )

                common = keywords1.intersection(keywords2)

                score += len(common) * 20

                score += min(
                    p1.publications or 0,
                    p2.publications or 0
                )

                score += min(
                    p1.patents or 0,
                    p2.patents or 0
                ) * 3

                if score > 0:

                    collaborations.append({

                        "researcher_1": p1.organization,

                        "researcher_2": p2.organization,

                        "domain": p1.research_domain,

                        "common_keywords": list(common),

                        "collaboration_score": score

                    })

        collaborations.sort(
            key=lambda x: x["collaboration_score"],
            reverse=True
        )

        return collaborations