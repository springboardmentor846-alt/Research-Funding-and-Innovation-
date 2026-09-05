from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CollaborationRequestCreate(BaseModel):
    receiver_id: int
    message: Optional[str] = None


class CollaborationRequestResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    message: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CollaborationRequestStatusUpdate(BaseModel):
    status: str  # "accepted" or "rejected"