from pydantic import BaseModel


class FundingSearchRequest(BaseModel):
    keyword: str


class FundingResult(BaseModel):
    opportunity_id: str
    opportunity_number: str
    title: str
    agency: str
    close_date: str
    funding_amount: str


class FundingDetailRequest(BaseModel):
    opportunity_id: str


class FundingBookmarkRequest(BaseModel):
    opportunity_id: str
    opportunity_number: str
    title: str
    agency: str
    close_date: str
class FundingAnalyticsRequest(BaseModel):
    keyword: str
    size: int = 100
class FundingAIInsightRequest(BaseModel):
    opportunity_id: str
class FundingProposalRequest(BaseModel):
    opportunity_id: str
    project_title: str
    project_description: str
    organization_name: str
class FundingRecommendationRequest(BaseModel):
    project_title: str
    project_description: str
    keyword: str
    size: int = 20

class FundingDeadlineRequest(BaseModel):
    keyword: str
    size: int = 20