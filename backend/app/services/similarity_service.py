import numpy as np

from sqlalchemy.orm import Session

from app.models.research_paper import ResearchPaper


class SimilarityService:

    def find_similar(
        self,
        db: Session,
        paper_id: int
    ):

        target = db.query(ResearchPaper).filter(
            ResearchPaper.id == paper_id
        ).first()

        if not target:

            return []

        if not target.embedding:

            return []

        target_vector = np.array(target.embedding)

        results = []

        papers = db.query(ResearchPaper).all()

        for paper in papers:

            if paper.id == target.id:

                continue

            if not paper.embedding:

                continue

            vector = np.array(paper.embedding)

            similarity = np.dot(
                target_vector,
                vector
            ) / (

                np.linalg.norm(target_vector)

                *

                np.linalg.norm(vector)

            )

            results.append({

                "paper_id": paper.id,

                "title": paper.title,

                "similarity": round(float(similarity), 4)

            })

        results.sort(

            key=lambda x: x["similarity"],

            reverse=True

        )

        return results[:10]