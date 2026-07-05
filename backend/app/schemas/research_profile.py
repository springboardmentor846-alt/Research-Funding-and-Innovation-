from pydantic import BaseModel


class ResearchProfileCreate(BaseModel):
    research_domain: str
    keywords: str
    publications: str
    patents: str
    technology_area: str
    organization: str


class ResearchProfileResponse(BaseModel):
    id: int
    user_id: int
    research_domain: str
    keywords: str
    publications: str
    patents: str
    technology_area: str
    organization: str

    class Config:
        from_attributes = True