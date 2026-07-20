from datetime import date

from pydantic import BaseModel, Field


class FundingOpportunityCreate(BaseModel):

    title: str = Field(
        min_length=2,
        max_length=500
    )

    organization: str = Field(
        min_length=2,
        max_length=255
    )

    funding_type: str | None = Field(
        default=None,
        max_length=100
    )

    research_domain: str | None = Field(
        default=None,
        max_length=255
    )

    description: str | None = Field(
        default=None,
        max_length=5000
    )

    funding_amount: str | None = Field(
        default=None,
        max_length=100
    )

    deadline: date | None = None

    official_link: str | None = Field(
        default=None,
        max_length=1000
    )

    country: str | None = Field(
        default=None,
        max_length=100
    )

    eligible_countries: str | None = None

    international_applicants_allowed: bool = False

    career_stage: str | None = Field(
        default=None,
        max_length=255
    )

    qualification: str | None = Field(
        default=None,
        max_length=255
    )

    experience_required: int | None = None

    keywords: str | None = None

    status: str = Field(
        default="Open",
        max_length=50
    )


class FundingOpportunityUpdate(BaseModel):

    title: str | None = Field(
        default=None,
        min_length=2,
        max_length=500
    )

    organization: str | None = Field(
        default=None,
        max_length=255
    )

    funding_type: str | None = Field(
        default=None,
        max_length=100
    )

    research_domain: str | None = Field(
        default=None,
        max_length=255
    )

    description: str | None = Field(
        default=None,
        max_length=5000
    )

    funding_amount: str | None = Field(
        default=None,
        max_length=100
    )

    deadline: date | None = None

    official_link: str | None = Field(
        default=None,
        max_length=1000
    )

    country: str | None = Field(
        default=None,
        max_length=100
    )

    eligible_countries: str | None = None

    international_applicants_allowed: bool | None = None

    career_stage: str | None = Field(
        default=None,
        max_length=255
    )

    qualification: str | None = Field(
        default=None,
        max_length=255
    )

    experience_required: int | None = None

    keywords: str | None = None

    status: str | None = Field(
        default=None,
        max_length=50
    )