from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Report, FundingOpportunity, Patent, Publication, TechTrend
from app.schemas.schemas import ReportRead, ReportCreate
from app.services.report_generator import report_generator
from typing import List
from datetime import datetime

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("", response_model=List[ReportRead])
def list_reports(db: Session = Depends(get_db)):
    return db.query(Report).order_by(Report.created_at.desc()).all()

@router.post("/generate", response_model=ReportRead)
def generate_report(payload: ReportCreate, db: Session = Depends(get_db)):
    report = Report(
        title=payload.title,
        report_type=payload.report_type,
        format=payload.format,
        parameters=payload.parameters or {},
        file_url=f"/api/v1/reports/download/{payload.report_type.lower()}-digest.{payload.format.lower()}"
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

@router.get("/download/{filename}")
def download_report_file(filename: str, db: Session = Depends(get_db)):
    if "funding" in filename.lower():
        grants = db.query(FundingOpportunity).all()
        rows = [[g.id, g.title, g.agency, g.grant_type, g.amount, g.deadline] for g in grants]
        content = report_generator.generate_csv_report("Funding Intelligence Export", ["ID", "Title", "Agency", "Type", "Amount USD", "Deadline"], rows)
        return Response(content=content, media_type="text/csv", headers={"Content-Disposition": f"attachment; filename={filename}"})
    
    # Generic CSV export
    content = report_generator.generate_csv_report("Executive Platform Digest", ["Section", "Status", "Metric"], [["Research", "Active", "500+ Papers"], ["Patents", "Mapped", "300+ Grants"]])
    return Response(content=content, media_type="text/csv", headers={"Content-Disposition": f"attachment; filename={filename}"})
