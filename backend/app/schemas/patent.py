"""
Patent Landscape Analytics Pydantic Schemas
"""

from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, ConfigDict


class PatentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    patent_number: str
    title: str
    assignee: str
    filing_date: Optional[datetime] = None
    grant_date: Optional[datetime] = None
    ipc_classification: str
    technology_domain: str
    citation_count: int = 0
    abstract: Optional[str] = None
    claims_summary: Optional[str] = None
    cluster_id: Optional[str] = None
    patent_url: Optional[str] = None
    keywords: List[str] = []


class PatentClusterSummary(BaseModel):
    cluster_id: str
    cluster_name: str
    ipc_code: str
    patent_count: int
    top_assignees: List[str]
    sample_patents: List[PatentResponse]


class PatentLandscapeAnalytics(BaseModel):
    total_patents_analyzed: int
    top_assignees_breakdown: Dict[str, int]
    ipc_classification_distribution: Dict[str, int]
    technology_domain_breakdown: Dict[str, int]
    patent_clusters: List[PatentClusterSummary]
