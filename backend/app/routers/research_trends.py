from fastapi import APIRouter

from app.services.research_trends_service import (
    fetch_openalex,
    publication_trend,
    country_statistics,
    university_statistics,
    topic_graph,
    ai_insight,
)

from app.schemas.research_trends import ResearchTrendResponse
router = APIRouter(
    prefix="/research-trends",
    tags=["Research Trends"]
)


@router.get("/", response_model=ResearchTrendResponse)
def analyze_topic(query: str):

    data = fetch_openalex(query)

    trend = publication_trend(data)
    countries = country_statistics(data)
    universities = university_statistics(data)
    graph = topic_graph(data)

    insight = ai_insight(
        query,
        trend,
        countries,
        universities
    )

    return {
        "query": query,
        "trend": trend,
        "countries": countries,
        "universities": universities,
        "topicGraph": graph,
        "aiInsight": insight
    }