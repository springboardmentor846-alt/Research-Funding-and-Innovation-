from typing import Optional

from pydantic import BaseModel, ConfigDict, HttpUrl


class PrototypeDetailBase(BaseModel):
    prototype_name: str
    prototype_type: Optional[str] = None
    development_stage: Optional[str] = None
    prototype_url: Optional[HttpUrl] = None
    demo_video_url: Optional[HttpUrl] = None
    description: Optional[str] = None


class PrototypeDetailCreate(PrototypeDetailBase):
    pass


class PrototypeDetailUpdate(BaseModel):
    prototype_name: Optional[str] = None
    prototype_type: Optional[str] = None
    development_stage: Optional[str] = None
    prototype_url: Optional[HttpUrl] = None
    demo_video_url: Optional[HttpUrl] = None
    description: Optional[str] = None


class PrototypeDetailResponse(PrototypeDetailBase):
    id: int
    portfolio_id: int

    model_config = ConfigDict(from_attributes=True)