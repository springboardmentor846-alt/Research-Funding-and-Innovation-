from pydantic import BaseModel


class PublicationCreate(BaseModel):
    title: str
    authors: str
    journal: str
    year: int
    doi: str
    citation_count: int
    research_domain: str