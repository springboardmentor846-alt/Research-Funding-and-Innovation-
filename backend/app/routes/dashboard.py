from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import verify_token,role_required

from app.models.publication import Publication
from app.models.research_interest import ResearchInterest
from app.models.academic_profile import AcademicProfile
from app.models.research_history import ResearchHistory
from app.models.user import User
from app.models.research_profile import ResearchProfile
from app.models.proposal import Proposal
from sqlalchemy import func

from app.models.funding import FundingOpportunity
from app.models.patent import Patent
from app.models.innovation_score import InnovationScore
from app.models.commercialization import Commercialization

router = APIRouter(
    tags=["Dashboard"]
)
@router.get("/dashboard")
def researcher_dashboard(
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):

    user = db.query(User).filter(
        User.email == current_user["sub"]
    ).first()

    total_profiles = db.query(ResearchProfile).filter(
        ResearchProfile.user_id == user.id
    ).count()

    total_proposals = db.query(Proposal).filter(
        Proposal.user_id == user.id
    ).count()

    approved = db.query(Proposal).filter(
        Proposal.user_id == user.id,
        Proposal.status.ilike("approved")
    ).count()

    pending = db.query(Proposal).filter(
        Proposal.user_id == user.id,
        Proposal.status.ilike("pending")
    ).count()

    publications = db.query(Publication).filter(
        Publication.user_id == user.id
    ).count()

    interests = db.query(ResearchInterest).filter(
        ResearchInterest.user_id == user.id
    ).count()

    research_history = db.query(ResearchHistory).filter(
        ResearchHistory.user_id == user.id
    ).count()

    academic_profile = db.query(AcademicProfile).filter(
        AcademicProfile.user_id == user.id
    ).first()

    return {
        "Researcher": user.full_name,
        "Email": user.email,

        "Research Profiles": total_profiles,
        "Research Interests": interests,
        "Publications": publications,
        "Research Projects": research_history,

        "Academic Profile Available": academic_profile is not None,

        "Submitted Proposals": total_proposals,
        "Approved Proposals": approved,
        "Pending Proposals": pending
    }

@router.get("/dashboard/platform")
def platform_dashboard(
    db: Session = Depends(get_db)
):

    return {

        "Total Users":
            db.query(User).count(),

        "Research Profiles":
            db.query(ResearchProfile).count(),

        "Publications":
            db.query(Publication).count(),

        "Patents":
            db.query(Patent).count(),

        "Funding Opportunities":
            db.query(FundingOpportunity).count(),

        "Innovation Assessments":
            db.query(InnovationScore).count(),

        "Commercialization Projects":
            db.query(Commercialization).count()

    }

@router.get("/dashboard/funding")
def funding_dashboard(
    db: Session = Depends(get_db)
):

    total_amount = db.query(
        func.sum(FundingOpportunity.funding_amount)
    ).scalar()

    return {

        "Funding Opportunities":
            db.query(FundingOpportunity).count(),

        "Total Funding Amount":
            total_amount or 0

    }

@router.get("/dashboard/innovation")
def innovation_dashboard(
    db: Session = Depends(get_db)
):

    average = db.query(
        func.avg(InnovationScore.innovation_score)
    ).scalar()

    highest = db.query(
        InnovationScore
    ).order_by(
        InnovationScore.innovation_score.desc()
    ).first()

    return {

        "Average Innovation Score":
            round(average or 0, 2),

        "Highest Innovation Score":
            highest.innovation_score if highest else 0,

        "Top Researcher":
            highest.researcher_email if highest else None

    }

@router.get("/dashboard/commercialization")
def commercialization_dashboard(
    db: Session = Depends(get_db)
):

    average = db.query(
        func.avg(
            Commercialization.commercialization_score
        )
    ).scalar()

    return {

        "Commercialization Projects":
            db.query(Commercialization).count(),

        "Average Commercialization Score":
            round(average or 0, 2)

    }

@router.get("/dashboard/research")
def research_dashboard_summary(
    db: Session = Depends(get_db)
):

    return {

        "Research Profiles":
            db.query(ResearchProfile).count(),

        "Research Interests":
            db.query(ResearchInterest).count(),

        "Research Histories":
            db.query(ResearchHistory).count(),

        "Academic Profiles":
            db.query(AcademicProfile).count(),

        "Publications":
            db.query(Publication).count(),

        "Patents":
            db.query(Patent).count()

    }