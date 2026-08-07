"""
Pydantic schemas for Notifications, Reports, Admin Statistics, System Analytics, and User Management.
"""
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class NotificationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    message: str
    notification_type: str
    is_read: bool
    link_url: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationListResponse(BaseModel):
    notifications: List[NotificationResponse]
    unread_count: int


class ReportGenerateRequest(BaseModel):
    report_type: str = "research_summary"  # research_summary, funding, patent, innovation_score
    title: Optional[str] = None
    format: str = "pdf"  # pdf, csv


class ReportResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    report_type: str
    title: str
    format: str
    summary: Optional[str] = None
    data_json: Dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminDashboardStatsResponse(BaseModel):
    total_users: int
    research_profiles: int
    funding_opportunities: int
    research_papers: int
    patents: int
    technology_trends: int
    commercialization_opportunities: int
    active_collaborations: int


class DomainDistributionItem(BaseModel):
    domain: str
    count: int
    percentage: float


class ChartSeriesItem(BaseModel):
    label: str
    value: float


class SystemAnalyticsResponse(BaseModel):
    user_growth: List[ChartSeriesItem]
    domain_distribution: List[DomainDistributionItem]
    funding_distribution: List[ChartSeriesItem]
    patent_statistics: List[ChartSeriesItem]
    innovation_score_distribution: List[ChartSeriesItem]


class AdminUserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    role: str
    is_active: bool
    is_verified: bool
    organization: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminUserUpdateStatusRequest(BaseModel):
    is_active: Optional[bool] = None
    role: Optional[str] = None
