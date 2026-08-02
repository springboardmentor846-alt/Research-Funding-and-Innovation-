from pydantic import BaseModel


class PatentSearchRequest(BaseModel):
    query: str
    size: int = 10


class PatentResult(BaseModel):
    lens_id: str
    title: str
    applicant: str
    inventor: str
    publication_date: str
    jurisdiction: str
    legal_status: str


class PatentBookmarkRequest(BaseModel):
    lens_id: str
    title: str
    applicant: str
    jurisdiction: str

class SimilarPatentResult(BaseModel):
    lens_id: str
    title: str
    applicant: str
    publication_date: str
    jurisdiction: str
class PatentAnalyticsRequest(BaseModel):
    query: str
    size: int = 100
class PatentComparisonRequest(BaseModel):
    lens_id_1: str
    lens_id_2: str
class PatentTimelineRequest(BaseModel):
    lens_id: str
class PatentInsightRequest(BaseModel):
    lens_id: str