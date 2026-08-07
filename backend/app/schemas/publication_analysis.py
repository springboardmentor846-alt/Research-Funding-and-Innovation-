from pydantic import BaseModel

class PublicationSummary(BaseModel):

    total_researchers: int

    total_publications: int

    average_publications: float

    top_domains: list

    organization_publications: dict