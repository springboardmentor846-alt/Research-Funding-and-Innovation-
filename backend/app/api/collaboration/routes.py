from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.core.security import get_current_user
from app.crud.user import get_user_by_email
from app.schemas.collaboration_request import (
    CollaborationRequestCreate,
    CollaborationRequestResponse,
    CollaborationRequestStatusUpdate,
)
from app.crud.collaboration_request import (
    create_collaboration_request,
    get_received_requests,
    get_sent_requests,
    get_all_requests_for_user,
    get_request_by_id,
    update_request_status,
)

router = APIRouter()


def _current_db_user(db: Session, current_user: dict):
    email = current_user.get("sub")
    db_user = get_user_by_email(db, email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.post("/", response_model=CollaborationRequestResponse)
def send_collaboration_request(
    data: CollaborationRequestCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    sender = _current_db_user(db, current_user)

    if sender.id == data.receiver_id:
        raise HTTPException(status_code=400, detail="You cannot send a collaboration request to yourself")

    receiver = db.query(type(sender)).filter(type(sender).id == data.receiver_id).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver user not found")

    return create_collaboration_request(db, sender.id, data.receiver_id, data.message)


@router.get("/received", response_model=List[CollaborationRequestResponse])
def list_received_requests(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user = _current_db_user(db, current_user)
    return get_received_requests(db, user.id)


@router.get("/sent", response_model=List[CollaborationRequestResponse])
def list_sent_requests(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user = _current_db_user(db, current_user)
    return get_sent_requests(db, user.id)


@router.get("/", response_model=List[CollaborationRequestResponse])
def list_all_requests(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user = _current_db_user(db, current_user)
    return get_all_requests_for_user(db, user.id)


@router.patch("/{request_id}", response_model=CollaborationRequestResponse)
def respond_to_request(
    request_id: int,
    payload: CollaborationRequestStatusUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user = _current_db_user(db, current_user)
    request_obj = get_request_by_id(db, request_id)

    if not request_obj:
        raise HTTPException(status_code=404, detail="Collaboration request not found")

    if request_obj.receiver_id != user.id:
        raise HTTPException(status_code=403, detail="Only the receiver can respond to this request")

    if payload.status not in ("accepted", "rejected"):
        raise HTTPException(status_code=400, detail="Status must be 'accepted' or 'rejected'")

    return update_request_status(db, request_obj, payload.status)