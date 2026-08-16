from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies.auth_deps import get_current_user
from app.models.models import Notification, User
from app.schemas.schemas import NotificationRead
from app.services.websocket_manager import ws_manager
from typing import List

router = APIRouter(prefix="/notifications", tags=["Notifications & Real-time WebSockets"])

@router.get("", response_model=List[NotificationRead])
def list_user_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Notification).filter(Notification.user_id == current_user.id).order_by(Notification.created_at.desc()).all()

@router.put("/{notification_id}/read")
def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notif = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == current_user.id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found.")
    notif.is_read = True
    db.commit()
    return {"message": "Notification marked as read."}

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, user_id: int = 1):
    await ws_manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo or process incoming socket messages
            await websocket.send_json({"type": "pong", "message": f"Server received: {data}"})
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, user_id)
