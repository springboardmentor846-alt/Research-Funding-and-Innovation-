from pydantic import BaseModel


class ProfileCreate(BaseModel):
    organization: str
    designation: str
    research_domain: str
    keywords: str
    biography: str


class ProfileResponse(ProfileCreate):
    id: int

    class Config:
        from_attributes = True