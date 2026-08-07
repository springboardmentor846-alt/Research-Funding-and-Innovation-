from pydantic import BaseModel


class ResearchIntelligence(BaseModel):

    researcher: str

    research_domain: str

    technology_area: str

    organization: str

    publications: int

    patents: int

    experience: int

    recommended_funding: int

    best_grant: dict

    total_publications: int

    total_patents: int

    top_research_domain: list

    top_organizations: list