from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import verify_token
import pandas as pd
from app.models.user import User
from app.models.report import Report
from openpyxl import Workbook
from app.schemas.report import ReportCreate
from sqlalchemy import func
from fastapi.responses import FileResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import os

router = APIRouter(
    tags=["Reports"]
)

@router.post("/reports")
def generate_report(
    report: ReportCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):

    user = db.query(User).filter(
        User.email == current_user["sub"]
    ).first()

    if not user:
        return {"message": "User not found"}

    filename = (
        report.report_type.replace(" ", "_")
        + "."
        + report.file_format.lower()
    )

    new_report = Report(
        user_id=user.id,
        report_type=report.report_type,
        file_format=report.file_format,
        file_name=filename
    )

    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    return {
        "message": "Report Generated Successfully",
        "report_id": new_report.id,
        "file_name": filename
    }

@router.get("/reports")
def my_reports(
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):

    user = db.query(User).filter(
        User.email == current_user["sub"]
    ).first()

    return db.query(Report).filter(
        Report.user_id == user.id
    ).all()

@router.get("/reports/pdf")
def export_pdf(
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):

    user = db.query(User).filter(
        User.email == current_user["sub"]
    ).first()

    reports = db.query(Report).filter(
        Report.user_id == user.id
    ).all()

    os.makedirs("generated_reports", exist_ok=True)

    filename = f"generated_reports/{user.id}_report.pdf"

    doc = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()

    story = []

    story.append(Paragraph("Research Funding Platform Report", styles["Heading1"]))

    story.append(Paragraph(f"User : {user.name}", styles["Normal"]))

    story.append(Paragraph(f"Email : {user.email}", styles["Normal"]))

    story.append(Paragraph("<br/>Generated Reports", styles["Heading2"]))

    for report in reports:

        story.append(
            Paragraph(
                f"{report.report_type} ({report.file_format})",
                styles["Normal"]
            )
        )

    doc.build(story)

    return FileResponse(
        filename,
        media_type="application/pdf",
        filename="Research_Report.pdf"
    )

@router.get("/reports/excel")
def export_excel(
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):

    user = db.query(User).filter(
        User.email == current_user["sub"]
    ).first()

    reports = db.query(Report).filter(
        Report.user_id == user.id
    ).all()

    os.makedirs("generated_reports", exist_ok=True)

    filename = f"generated_reports/{user.id}_report.xlsx"

    wb = Workbook()

    ws = wb.active

    ws.append([
        "Report Type",
        "Format",
        "Status"
    ])

    for report in reports:

        ws.append([
            report.report_type,
            report.file_format,
            report.status
        ])

    wb.save(filename)

    return FileResponse(
        filename,
        filename="Research_Report.xlsx"
    )

@router.get("/reports/csv")
def export_csv(
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):

    user = db.query(User).filter(
        User.email == current_user["sub"]
    ).first()

    reports = db.query(Report).filter(
        Report.user_id == user.id
    ).all()

    os.makedirs("generated_reports", exist_ok=True)

    filename = f"generated_reports/{user.id}_report.csv"

    data = []

    for report in reports:

        data.append({

            "Report Type": report.report_type,

            "Format": report.file_format,

            "Status": report.status

        })

    pd.DataFrame(data).to_csv(
        filename,
        index=False
    )

    return FileResponse(
        filename,
        filename="Research_Report.csv"
    )

@router.get("/reports/statistics")
def report_statistics(
    db: Session = Depends(get_db)
):

    return {

        "Total Reports":
            db.query(Report).count(),

        "PDF Reports":
            db.query(Report).filter(
                Report.file_format == "PDF"
            ).count(),

        "Excel Reports":
            db.query(Report).filter(
                Report.file_format == "Excel"
            ).count(),

        "CSV Reports":
            db.query(Report).filter(
                Report.file_format == "CSV"
            ).count()

    }