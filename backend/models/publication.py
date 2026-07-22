from pydantic import BaseModel

class Publication(BaseModel):
    email: str
    title: str
    authors: str
    journal: str
    publication_year: int