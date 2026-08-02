from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.innovation_vault import (
    DocumentType,
    Visibility,
)


# -----------------------------
# Create Schema
# -----------------------------
class InnovationVaultCreate(BaseModel):
    portfolio_id: int
    title: str
    description: Optional[str] = None
    document_type: DocumentType
    visibility: Visibility = Visibility.PRIVATE
    nda_required: bool = False


# -----------------------------
# Update Schema
# -----------------------------
class InnovationVaultUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    visibility: Optional[Visibility] = None
    nda_required: Optional[bool] = None


# -----------------------------
# Response Schema
# -----------------------------
class InnovationVaultResponse(BaseModel):
    id: int
    user_id: int
    portfolio_id: int

    title: str
    description: Optional[str]

    document_type: DocumentType

    original_filename: str
    stored_filename: str
    file_path: str
    file_extension: str
    file_size: int
    mime_type: str

    visibility: Visibility
    nda_required: bool

    uploaded_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True