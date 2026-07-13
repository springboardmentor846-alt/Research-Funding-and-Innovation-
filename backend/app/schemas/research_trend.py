from pydantic import BaseModel


class ResearchTrendCreate(BaseModel):
    title: str
    research_domain: str
    publication_year: int
    citation_count: int
    hotspot_score: int
    trend_level: str