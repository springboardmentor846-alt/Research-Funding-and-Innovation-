from pydantic import BaseModel
from datetime import date


class GrantCreate(BaseModel):
    title: str
    description: str
    funding_amount: float
    deadline: date
    organization: str
    eligibility: str


class GrantResponse(GrantCreate):
    id: int
    status: str

    class Config:
        from_attributes = True