from typing import Optional

from pydantic import BaseModel, HttpUrl, ConfigDict


class ProjectDetailBase(BaseModel):
    github_url: Optional[HttpUrl] = None
    demo_url: Optional[HttpUrl] = None
    technology_stack: Optional[str] = None
    team_size: Optional[int] = None
    project_duration: Optional[str] = None


class ProjectDetailCreate(ProjectDetailBase):
    pass


class ProjectDetailUpdate(ProjectDetailBase):
    pass


class ProjectDetailResponse(ProjectDetailBase):
    id: int
    portfolio_id: int

    model_config = ConfigDict(from_attributes=True)