from pydantic import BaseModel

class ResearchProfile(BaseModel):
    email: str
    research_domain: str
    keywords: str
    publications: int
    patents: int
    technology_area: str
    organization: str