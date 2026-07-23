from sqlalchemy.orm import Session
from app.models.research_project import ResearchProject
from app.models.user import User


def get_dashboard_data(db, current_user):
    role = current_user["role"]

    if role == "Researcher":
        total_projects = (
            db.query(ResearchProject)
            .filter(
                ResearchProject.created_by == current_user["id"]
            )
            .count()
        )

        return {
            "role": role,
            "dashboard": {
                "my_projects": total_projects,
                "available_grants": "Coming Soon",
                "research_trends": "Coming Soon"
            }
        }

    elif role == "Investor":
        return {
            "role": role,
            "dashboard": {
                "innovation_opportunities": "Coming Soon",
                "recommended_startups": "Coming Soon"
            }
        }

    elif role == "University":
        return {
            "role": role,
            "dashboard": {
                "research_portfolios": "Coming Soon",
                "active_researchers": "Coming Soon"
            }
        }

    elif role == "Admin":

        total_users = db.query(User).count()

        total_projects = db.query(
            ResearchProject
        ).count()

        return {
            "role": role,
            "dashboard": {
                "total_users": total_users,
                "total_projects": total_projects
            }
        }

    return {
        "message": "Dashboard Not Available"
    }