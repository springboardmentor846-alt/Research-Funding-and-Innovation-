from pydantic import BaseModel


class ResearchProfileCreate(BaseModel):
    research_domain: str
    keywords: str
    publications: int
    patents: int
    technology_area: str
    organization: str
    experience: int