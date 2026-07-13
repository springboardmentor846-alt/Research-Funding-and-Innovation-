from pydantic import BaseModel


class PatentCreate(BaseModel):
    title: str
    assignee: str
    filing_date: str
    patent_classification: str
    technology_domain: str
    citation_count: int