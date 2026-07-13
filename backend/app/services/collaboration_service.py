from sqlalchemy.orm import Session

from app.models.research_profile import ResearchProfile


class CollaborationService:

    def recommend(self, db: Session, profile_id: int):

        target = db.query(ResearchProfile).filter(
            ResearchProfile.id == profile_id
        ).first()

        if not target:
            return []

        profiles = db.query(ResearchProfile).all()

        recommendations = []

        target_keywords = {
            keyword.strip().lower()
            for keyword in (target.keywords or "").split(",")
            if keyword.strip()
        }

        for profile in profiles:

            if profile.id == target.id:
                continue

            profile_keywords = {
                keyword.strip().lower()
                for keyword in (profile.keywords or "").split(",")
                if keyword.strip()
            }

            common_keywords = len(
                target_keywords.intersection(profile_keywords)
            )

            domain_bonus = 50 if (
                profile.research_domain == target.research_domain
            ) else 0

            score = (
                common_keywords * 25 +
                domain_bonus +
                min(profile.publications or 0, 30) * 2 +
                min(profile.patents or 0, 20) * 4 +
                min(profile.experience or 0, 20)
            )

            recommendations.append({

                "profile_id": profile.id,

                "organization": profile.organization,

                "research_domain": profile.research_domain,

                "keywords": profile.keywords,

                "publications": profile.publications,

                "patents": profile.patents,

                "experience": profile.experience,

                "common_keywords": common_keywords,

                "collaboration_score": score

            })

        recommendations.sort(
            key=lambda x: x["collaboration_score"],
            reverse=True
        )

        return recommendations[:10]