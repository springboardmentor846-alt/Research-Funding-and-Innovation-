"""
Role-Based Dashboard Pydantic Schemas
"""

from typing import List, Dict, Any
from pydantic import BaseModel


class ResearcherDashboardMetrics(BaseModel):
    recommended_grants_count: int
    active_publications_count: int
    patents_indexed_count: int
    user_innovation_score: float
    funding_recommendations: List[Dict[str, Any]]
    research_trends_summary: List[Dict[str, Any]]
    recent_patent_insights: List[Dict[str, Any]]


class StartupDashboardMetrics(BaseModel):
    open_funding_calls: int
    technology_opportunities_count: int
    competitor_patents_count: int
    commercialization_readiness_score: float
    funding_opportunities: List[Dict[str, Any]]
    technology_opportunities: List[Dict[str, Any]]
    patent_intelligence: List[Dict[str, Any]]
    commercialization_insights: List[Dict[str, Any]]


class ManagerDashboardMetrics(BaseModel):
    portfolio_projects_count: int
    active_pipeline_stage_counts: Dict[str, int]
    monitored_tech_trends_count: int
    total_funding_tracked: float
    portfolio_analytics: Dict[str, Any]
    innovation_pipeline: List[Dict[str, Any]]
    technology_trend_monitoring: List[Dict[str, Any]]
    funding_analytics: Dict[str, Any]


class AdminDashboardMetrics(BaseModel):
    total_registered_users: int
    role_distribution: Dict[str, int]
    system_health_status: str
    total_grants_indexed: int
    total_patents_indexed: int
    total_publications_indexed: int
    platform_analytics: Dict[str, Any]
