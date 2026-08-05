from pydantic import BaseModel


class TrendPoint(BaseModel):
    year: int
    count: int


class CountryStat(BaseModel):
    country: str
    count: int


class UniversityStat(BaseModel):
    university: str
    count: int


class TopicNode(BaseModel):
    id: str
    label: str


class TopicEdge(BaseModel):
    source: str
    target: str


class TopicGraph(BaseModel):
    nodes: list[TopicNode]
    edges: list[TopicEdge]


class ResearchTrendResponse(BaseModel):
    query: str
    trend: list[TrendPoint]
    countries: list[CountryStat]
    universities: list[UniversityStat]
    topicGraph: TopicGraph
    aiInsight: str