from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.collaboration_request import CollaborationRequest


def create_collaboration_request(db: Session, sender_id: int, receiver_id: int, message: str | None):
    req = CollaborationRequest(
        sender_id=sender_id,
        receiver_id=receiver_id,
        message=message,
        status="pending",
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


def get_received_requests(db: Session, user_id: int):
    return (
        db.query(CollaborationRequest)
        .filter(CollaborationRequest.receiver_id == user_id)
        .order_by(CollaborationRequest.created_at.desc())
        .all()
    )


def get_sent_requests(db: Session, user_id: int):
    return (
        db.query(CollaborationRequest)
        .filter(CollaborationRequest.sender_id == user_id)
        .order_by(CollaborationRequest.created_at.desc())
        .all()
    )


def get_all_requests_for_user(db: Session, user_id: int):
    return (
        db.query(CollaborationRequest)
        .filter(
            or_(
                CollaborationRequest.sender_id == user_id,
                CollaborationRequest.receiver_id == user_id,
            )
        )
        .order_by(CollaborationRequest.created_at.desc())
        .all()
    )


def get_request_by_id(db: Session, request_id: int):
    return db.query(CollaborationRequest).filter(CollaborationRequest.id == request_id).first()


def update_request_status(db: Session, request: CollaborationRequest, status: str):
    request.status = status
    db.commit()
    db.refresh(request)
    return request