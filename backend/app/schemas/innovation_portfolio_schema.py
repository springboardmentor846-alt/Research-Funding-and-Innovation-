from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, HttpUrl


class PortfolioCategory(str, Enum):
    RESEARCH_PAPER = "Research Paper"
    PROJECT = "Project"
    PATENT = "Patent"
    PROTOTYPE = "Prototype"


class PortfolioStatus(str, Enum):
    ONGOING = "Ongoing"
    COMPLETED = "Completed"
    PUBLISHED = "Published"
    FILED = "Filed"


class InnovationPortfolioBase(BaseModel):
    title: str
    category: PortfolioCategory
    description: Optional[str] = None
    technology_stack: Optional[str] = None
    collaborators: Optional[str] = None
    github_url: Optional[HttpUrl] = None
    paper_url: Optional[HttpUrl] = None
    patent_number: Optional[str] = None
    prototype_link: Optional[HttpUrl] = None
    status: PortfolioStatus


class InnovationPortfolioCreate(InnovationPortfolioBase):
    pass


class InnovationPortfolioUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[PortfolioCategory] = None
    description: Optional[str] = None
    technology_stack: Optional[str] = None
    collaborators: Optional[str] = None
    github_url: Optional[HttpUrl] = None
    paper_url: Optional[HttpUrl] = None
    patent_number: Optional[str] = None
    prototype_link: Optional[HttpUrl] = None
    status: Optional[PortfolioStatus] = None


class InnovationPortfolioResponse(InnovationPortfolioBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)