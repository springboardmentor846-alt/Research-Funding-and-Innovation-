from pydantic import BaseModel


class PatentBase(BaseModel):
    patent_title: str
    abstract: str
    assignee: str
    filing_date: str
    patent_classification: str
    technology_domain: str
    citation_count: int
    country: str
    status: str


class PatentCreate(PatentBase):
    pass


class PatentUpdate(PatentBase):
    pass


class PatentResponse(PatentBase):
    id: int

    class Config:
        from_attributes = True