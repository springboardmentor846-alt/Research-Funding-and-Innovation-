from datetime import datetime

from pydantic import BaseModel, Field


class CollaborationRequestCreate(BaseModel):
    recipient_user_id: int
    message: str = Field(default="", max_length=2000)


class CollaborationRequestUpdate(BaseModel):
    status: str


class CollaborationRequestResponse(BaseModel):
    id: int
    sender_user_id: int
    recipient_user_id: int
    sender_name: str
    recipient_name: str
    sender_role: str
    recipient_role: str
    message: str
    status: str
    created_at: datetime
