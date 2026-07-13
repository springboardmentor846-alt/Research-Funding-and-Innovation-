from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.patent import Patent


class PatentLandscapeService:

    def analytics(self, db: Session):

        domains = (
            db.query(
                Patent.technology_domain,
                func.count(Patent.id)
            )
            .group_by(Patent.technology_domain)
            .all()
        )

        assignees = (
            db.query(
                Patent.assignee,
                func.count(Patent.id)
            )
            .group_by(Patent.assignee)
            .order_by(func.count(Patent.id).desc())
            .limit(10)
            .all()
        )

        return {
    "total_patents": db.query(Patent).count(),

    "technology_domains": [
        {
            "domain": d[0],
            "patents": d[1]
        }
        for d in domains
    ],

    "top_assignees": [
        {
            "assignee": a[0],
            "patents": a[1]
        }
        for a in assignees
    ],

    "most_active_domain":
        max(domains, key=lambda x: x[1])[0]
        if domains else None,

    "largest_patent_holder":
        assignees[0][0]
        if assignees else None
}