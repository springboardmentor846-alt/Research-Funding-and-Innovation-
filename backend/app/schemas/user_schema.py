from typing import Literal

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str

    role: Literal[
        "Researcher",
        "Investor",
        "Startup Founder",
        "University",
        "Funding Agency",
        "Industry Partner"
    ]