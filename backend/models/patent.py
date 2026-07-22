from pydantic import BaseModel
from datetime import date

class Patent(BaseModel):
    email: str
    patent_title: str
    patent_number: str
    technology_domain: str
    filing_date: date