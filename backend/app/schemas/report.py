from pydantic import BaseModel


class ReportCreate(BaseModel):

    report_type: str

    file_format: str