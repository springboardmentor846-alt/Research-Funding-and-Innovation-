from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict


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


class PortfolioVisibility(str, Enum):
    PUBLIC = "Public"
    PRIVATE = "Private"


class InnovationPortfolioBase(BaseModel):
    title: str
    category: PortfolioCategory
    description: Optional[str] = None
    status: PortfolioStatus
    visibility: PortfolioVisibility


class InnovationPortfolioCreate(InnovationPortfolioBase):
    pass


class InnovationPortfolioUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[PortfolioCategory] = None
    description: Optional[str] = None
    status: Optional[PortfolioStatus] = None
    visibility: Optional[PortfolioVisibility] = None


class InnovationPortfolioResponse(InnovationPortfolioBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)