from pydantic import BaseModel


class ResearchInterestCreate(BaseModel):
    interest: str