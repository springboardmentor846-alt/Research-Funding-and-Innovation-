from pydantic import BaseModel


class AcademicProfileCreate(BaseModel):
    highest_degree: str
    university: str
    department: str
    designation: str
    years_experience: int