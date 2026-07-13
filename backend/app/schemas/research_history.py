from pydantic import BaseModel


class ResearchHistoryCreate(BaseModel):
    project_name: str
    funding_agency: str
    duration: str
    status: str
    description: str