from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import verify_token

from app.models.user import User
from app.models.research_history import ResearchHistory

from app.schemas.research_history import ResearchHistoryCreate

router = APIRouter(
    tags=["Research History"]
)


@router.post("/research-history")
def create_research_history(
    history: ResearchHistoryCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):

    user = db.query(User).filter(
        User.email == current_user["sub"]
    ).first()

    project = ResearchHistory(
        user_id=user.id,
        project_name=history.project_name,
        funding_agency=history.funding_agency,
        duration=history.duration,
        status=history.status,
        description=history.description
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return {
        "message": "Research History Added Successfully",
        "history_id": project.id
    }


@router.get("/research-history")
def get_research_history(
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):

    user = db.query(User).filter(
        User.email == current_user["sub"]
    ).first()

    return db.query(ResearchHistory).filter(
        ResearchHistory.user_id == user.id
    ).all()


@router.put("/research-history/{history_id}")
def update_research_history(
    history_id: int,
    history: ResearchHistoryCreate,
    db: Session = Depends(get_db)
):

    project = db.query(ResearchHistory).filter(
        ResearchHistory.id == history_id
    ).first()

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Research History Not Found"
        )

    project.project_name = history.project_name
    project.funding_agency = history.funding_agency
    project.duration = history.duration
    project.status = history.status
    project.description = history.description

    db.commit()
    db.refresh(project)

    return {
        "message": "Research History Updated Successfully"
    }


@router.delete("/research-history/{history_id}")
def delete_research_history(
    history_id: int,
    db: Session = Depends(get_db)
):

    project = db.query(ResearchHistory).filter(
        ResearchHistory.id == history_id
    ).first()

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Research History Not Found"
        )

    db.delete(project)
    db.commit()

    return {
        "message": "Research History Deleted Successfully"
    }