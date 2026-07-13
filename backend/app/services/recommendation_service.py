import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from app.models.research_paper import ResearchPaper


class RecommendationService:

    def recommend(self, db, paper_id):

        papers = db.query(ResearchPaper).all()

        target = None

        for paper in papers:
            if paper.id == paper_id:
                target = paper
                break

        if target is None:
            return []

        if target.embedding is None:
            return []

        target_vector = np.array(target.embedding).reshape(1, -1)

        recommendations = []

        for paper in papers:

            if paper.id == target.id:
                continue

            if paper.embedding is None:
                continue

            score = cosine_similarity(
                target_vector,
                np.array(paper.embedding).reshape(1, -1)
            )[0][0]

            recommendations.append({
                "paper_id": paper.id,
                "title": paper.title,
                "similarity": round(float(score), 4),
                "trl_level": paper.trl_level,
                "github_stars": paper.github_stars
            })

        recommendations.sort(
            key=lambda x: x["similarity"],
            reverse=True
        )

        return recommendations[:10]
    