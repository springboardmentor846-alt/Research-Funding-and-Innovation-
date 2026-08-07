from pydantic import BaseModel


class FundingRecommendation(BaseModel):

    id: int

    title: str

    agency: str

    amount: int

    deadline: str

    match_score: int

    description: str