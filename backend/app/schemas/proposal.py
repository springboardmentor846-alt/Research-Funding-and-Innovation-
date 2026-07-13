from pydantic import BaseModel


class ProposalCreate(BaseModel):
    funding_id: int
    title: str
    abstract: str