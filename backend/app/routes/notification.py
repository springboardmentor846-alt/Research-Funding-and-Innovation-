from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db

from app.auth import verify_token

from app.models.user import User
from app.models.notification import Notification

from app.schemas.notification import NotificationCreate

router = APIRouter(
    tags=["Notifications"]
)


@router.post("/notifications")
def create_notification(
    notification: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):

    user = db.query(User).filter(
        User.email == current_user["sub"]
    ).first()

    if not user:
        return {"message": "User not found"}

    new_notification = Notification(
        user_id=user.id,
        title=notification.title,
        message=notification.message,
        notification_type=notification.notification_type
    )

    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)

    return {
        "message": "Notification Created Successfully",
        "notification_id": new_notification.id
    }