from pydantic import BaseModel

class GrantMatch(BaseModel):

    funding_title: str

    agency: str

    match_score: int

    eligibility: str

    reasons: list[str]

    deadline: str

    amount: int