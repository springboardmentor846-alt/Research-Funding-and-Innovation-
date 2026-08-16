from datetime import datetime
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user


router = APIRouter(
    prefix="/reports",
    tags=["Reports & Export"],
)


REPORT_TYPES = {
    "funding": "Funding Report",
    "patents": "Patent Report",
    "research-trends": "Research Trend Report",
    "innovation": "Innovation Intelligence Report",
    "commercialization": "Commercialization Report",
}


def get_report_data(report_type: str, db: Session):

    # Use existing analytics endpoints/data through the database.
    from app import models

    if report_type == "funding":

        rows = db.query(models.FundingOpportunity).all()

        headers = [
            "Title",
            "Agency",
            "Research Domain",
            "Technology Area",
            "Amount",
            "Deadline",
        ]

        data = []

        for row in rows:
            data.append([
                getattr(row, "title", ""),
                getattr(row, "funding_agency", ""),
                getattr(row, "research_domain", ""),
                getattr(row, "technology_area", ""),
                getattr(row, "amount", ""),
                getattr(row, "deadline", ""),
            ])

        return headers, data

    if report_type == "patents":

        rows = db.query(models.Patent).all()

        headers = [
            "Title",
            "Assignee",
            "Filing Date",
            "Patent Number",
            "Technology Domain",
        ]

        data = []

        for row in rows:
            data.append([
                getattr(row, "title", ""),
                getattr(row, "assignee", ""),
                getattr(row, "filing_date", ""),
                getattr(row, "patent_number", ""),
                getattr(row, "technology_domain", ""),
            ])

        return headers, data

    if report_type == "research-trends":

        rows = db.query(models.Publication).all()

        yearly = {}

        for row in rows:

            year = getattr(row, "publication_year", None)

            if year is None:
                year = getattr(row, "year", None)

            if year is None:
                continue

            yearly[year] = yearly.get(year, 0) + 1

        headers = [
            "Year",
            "Publications",
        ]

        data = [
            [year, count]
            for year, count in sorted(yearly.items())
        ]

        return headers, data

    if report_type == "innovation":

        publications = db.query(models.Publication).count()
        patents = db.query(models.Patent).count()

        # Same type of rule-based scoring approach used
        # by the innovation intelligence module.
        publication_score = min(publications * 5, 30)
        patent_score = min(patents * 10, 40)

        innovation_score = min(
            publication_score + patent_score,
            100,
        )

        headers = [
            "Metric",
            "Value",
        ]

        data = [
            ["Publications", publications],
            ["Patents", patents],
            ["Publication Score", publication_score],
            ["Patent Score", patent_score],
            ["Innovation Score", innovation_score],
        ]

        return headers, data

    if report_type == "commercialization":

        publications = db.query(models.Publication).count()
        patents = db.query(models.Patent).count()

        publication_score = min(publications * 5, 30)
        patent_score = min(patents * 10, 40)

        innovation_score = min(
            publication_score + patent_score,
            100,
        )

        recommendations = []

        if patents >= 5:
            recommendations.append([
                "Patent Licensing",
                "Patent portfolio is suitable for licensing opportunities.",
            ])

        if publications >= 5:
            recommendations.append([
                "Industry Collaboration",
                "Published research can be explored with industry partners.",
            ])

        if patents >= 3 and publications >= 3:
            recommendations.append([
                "Startup Opportunity",
                "Research portfolio indicates potential for a technology startup.",
            ])

        if innovation_score >= 70:
            recommendations.append([
                "Commercialization Grant",
                "Portfolio may qualify for commercialization opportunities.",
            ])

        if not recommendations:
            recommendations.append([
                "Research Enhancement",
                "Increase publications and patents to unlock more opportunities.",
            ])

        headers = [
            "Recommendation",
            "Reason",
        ]

        return headers, recommendations

    raise HTTPException(
        status_code=404,
        detail="Unknown report type",
    )


def generate_pdf(title, headers, rows):

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30,
    )

    styles = getSampleStyleSheet()

    story = [
        Paragraph(
            "Research Funding & Innovation Platform",
            styles["Title"],
        ),
        Spacer(1, 10),
        Paragraph(
            title,
            styles["Heading2"],
        ),
        Spacer(1, 6),
        Paragraph(
            "Generated: "
            + datetime.now().strftime("%d-%m-%Y %H:%M"),
            styles["Normal"],
        ),
        Spacer(1, 15),
    ]

    table_data = [
        [str(value) for value in headers]
    ]

    for row in rows:
        table_data.append([
            str(value) if value is not None else ""
            for value in row
        ])

    table = Table(
        table_data,
        repeatRows=1,
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#17233c"),
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white,
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold",
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor("#d9deea"),
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8,
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP",
            ),
        ])
    )

    story.append(table)

    document.build(story)

    return buffer.getvalue()


def generate_excel(title, headers, rows):

    buffer = BytesIO()

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Report"

    worksheet["A1"] = title
    worksheet["A1"].font = worksheet["A1"].font.copy(
        bold=True,
        size=16,
    )

    worksheet["A2"] = (
        "Generated: "
        + datetime.now().strftime("%d-%m-%Y %H:%M")
    )

    worksheet.append([])
    worksheet.append(headers)

    for cell in worksheet[4]:
        cell.font = cell.font.copy(
            bold=True
        )

    for row in rows:
        worksheet.append(row)

    worksheet.freeze_panes = "A5"

    for column in worksheet.columns:

        maximum = 0

        for cell in column:
            value = str(cell.value or "")

            if len(value) > maximum:
                maximum = len(value)

        worksheet.column_dimensions[
            column[0].column_letter
        ].width = min(maximum + 2, 40)

    workbook.save(buffer)

    return buffer.getvalue()


@router.get("/{report_type}/pdf")
def export_pdf(
    report_type: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    if report_type not in REPORT_TYPES:
        raise HTTPException(
            status_code=404,
            detail="Unknown report type",
        )

    headers, rows = get_report_data(
        report_type,
        db,
    )

    content = generate_pdf(
        REPORT_TYPES[report_type],
        headers,
        rows,
    )

    filename = (
        report_type
        + "_report_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
        + ".pdf"
    )

    return StreamingResponse(
        BytesIO(content),
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            f'attachment; filename="{filename}"'
        },
    )


@router.get("/{report_type}/excel")
def export_excel(
    report_type: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    if report_type not in REPORT_TYPES:
        raise HTTPException(
            status_code=404,
            detail="Unknown report type",
        )

    headers, rows = get_report_data(
        report_type,
        db,
    )

    content = generate_excel(
        REPORT_TYPES[report_type],
        headers,
        rows,
    )

    filename = (
        report_type
        + "_report_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
        + ".xlsx"
    )

    return StreamingResponse(
        BytesIO(content),
        media_type=(
            "application/"
            "vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
            f'attachment; filename="{filename}"'
        },
    )