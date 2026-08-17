from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_role
from app.models.collaboration_request import CollaborationRequest
from app.models.role import Role
from app.models.user import User
from app.schemas.collaboration_request import (
    CollaborationRequestCreate,
    CollaborationRequestResponse,
    CollaborationRequestUpdate,
)

router = APIRouter(prefix="/collaboration", tags=["Collaboration"])

ALLOWED_ROLES = {"researcher", "startup_founder"}


def role_name(db: Session, user: User) -> str:
    role = db.scalar(select(Role).where(Role.id == user.role_id))
    return role.name if role else "unknown"


def ensure_allowed_participant(db: Session, user: User):
    role = role_name(db, user)
    if role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=400,
            detail="Collaboration is available between researchers and startup founders.",
        )
    return role


def serialize(db: Session, item: CollaborationRequest):
    sender = db.get(User, item.sender_user_id)
    recipient = db.get(User, item.recipient_user_id)
    if not sender or not recipient:
        raise HTTPException(status_code=500, detail="Collaboration participant not found.")

    return CollaborationRequestResponse(
        id=item.id,
        sender_user_id=item.sender_user_id,
        recipient_user_id=item.recipient_user_id,
        sender_name=sender.full_name,
        recipient_name=recipient.full_name,
        sender_role=role_name(db, sender),
        recipient_role=role_name(db, recipient),
        message=item.message,
        status=item.status,
        created_at=item.created_at,
    )



@router.post("/requests", response_model=CollaborationRequestResponse)
def create_request(
    data: CollaborationRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("researcher", "startup_founder")),
):
    ensure_allowed_participant(db, current_user)

    recipient = db.get(User, data.recipient_user_id)
    if not recipient or not recipient.is_active:
        raise HTTPException(status_code=404, detail="Recipient not found.")
    if recipient.id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot send a request to yourself.")

    recipient_role = ensure_allowed_participant(db, recipient)
    if recipient_role == "unknown":
        raise HTTPException(status_code=400, detail="Invalid recipient.")

    # Do not allow duplicate pending requests in either direction.
    existing = db.scalar(
        select(CollaborationRequest).where(
            or_(
                and_(
                    CollaborationRequest.sender_user_id == current_user.id,
                    CollaborationRequest.recipient_user_id == recipient.id,
                ),
                and_(
                    CollaborationRequest.sender_user_id == recipient.id,
                    CollaborationRequest.recipient_user_id == current_user.id,
                ),
            ),
            CollaborationRequest.status == "pending",
        )
    )
    if existing:
        raise HTTPException(status_code=400, detail="A pending collaboration request already exists.")

    item = CollaborationRequest(
        sender_user_id=current_user.id,
        recipient_user_id=recipient.id,
        message=(data.message or "").strip(),
        status="pending",
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return serialize(db, item)


@router.get("/requests")
def list_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("researcher", "startup_founder")),
):
    ensure_allowed_participant(db, current_user)

    incoming = db.scalars(
        select(CollaborationRequest)
        .where(CollaborationRequest.recipient_user_id == current_user.id)
        .order_by(CollaborationRequest.created_at.desc())
    ).all()

    outgoing = db.scalars(
        select(CollaborationRequest)
        .where(CollaborationRequest.sender_user_id == current_user.id)
        .order_by(CollaborationRequest.created_at.desc())
    ).all()

    return {
        "incoming": [serialize(db, item).model_dump() for item in incoming],
        "outgoing": [serialize(db, item).model_dump() for item in outgoing],
    }


@router.patch("/requests/{request_id}", response_model=CollaborationRequestResponse)
def update_request(
    request_id: int,
    data: CollaborationRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("researcher", "startup_founder")),
):
    ensure_allowed_participant(db, current_user)

    item = db.get(CollaborationRequest, request_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Collaboration request not found.")

    if item.recipient_user_id != current_user.id and item.sender_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You cannot update this request.")

    if data.status not in {"accepted", "rejected", "cancelled"}:
        raise HTTPException(status_code=400, detail="Invalid request status.")

    if data.status in {"accepted", "rejected"} and item.recipient_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the recipient can accept or reject a request.")

    if item.status != "pending":
        raise HTTPException(status_code=400, detail="This request has already been processed.")

    item.status = data.status
    db.commit()
    db.refresh(item)
    return serialize(db, item)
