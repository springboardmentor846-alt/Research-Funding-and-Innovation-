"""
Reports & Export System API Endpoints (PDF & Excel/CSV)
"""

from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fpdf import FPDF

from app.dependencies.db import get_db
from app.models.funding import FundingOpportunity
from app.models.patent import Patent
from app.services.export_service import ExportService

reports_router = APIRouter(prefix="/reports", tags=["Reports & Export System"])


def build_pdf_bytes(title: str, headers: list[str], rows: list[list[str]]) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 12, title, ln=True)
    pdf.ln(4)
    pdf.set_font("Arial", size=10)

    effective_page_width = pdf.w - 2 * pdf.l_margin
    column_width = effective_page_width / max(len(headers), 1)

    pdf.set_fill_color(230, 244, 255)
    for header in headers:
        pdf.cell(column_width, 8, str(header), border=1, fill=True)
    pdf.ln()

    for row in rows:
        for cell in row:
            pdf.cell(column_width, 8, str(cell)[:45], border=1)
        pdf.ln()

    return pdf.output(dest='S').encode('latin1')


@reports_router.get("/funding/export/csv")
async def export_funding_csv(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FundingOpportunity))
    grants = result.scalars().all()

    headers = ["ID", "Title", "Agency", "Type", "Max Award", "Currency", "Status", "Deadline"]
    rows = [
        [
            g.id,
            g.title,
            g.agency,
            g.opportunity_type,
            g.max_award,
            g.currency,
            g.status,
            g.deadline.isoformat() if g.deadline else "N/A",
        ]
        for g in grants
    ]
    csv_content = ExportService.generate_csv_report(headers, rows)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=funding_opportunities_report.csv"},
    )


@reports_router.get("/funding/export/json")
async def export_funding_json(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FundingOpportunity))
    grants = result.scalars().all()

    records = [
        {
            "id": g.id,
            "title": g.title,
            "agency": g.agency,
            "opportunity_type": g.opportunity_type,
            "max_award": g.max_award,
            "currency": g.currency,
            "status": g.status,
            "deadline": g.deadline.isoformat() if g.deadline else None,
        }
        for g in grants
    ]
    return JSONResponse(content={"report": "funding", "items": records})


@reports_router.get("/funding/export/pdf")
async def export_funding_pdf(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FundingOpportunity).limit(20))
    grants = result.scalars().all()

    headers = ["Title", "Agency", "Type", "Max Award", "Status"]
    rows = [
        [
            g.title,
            g.agency,
            g.opportunity_type,
            f"{g.currency} {g.max_award:,}" if g.max_award is not None else "N/A",
            g.status,
        ]
        for g in grants
    ]

    pdf_bytes = build_pdf_bytes("Funding Opportunity Report", headers, rows)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=funding_opportunities_report.pdf"},
    )


@reports_router.get("/patents/export/csv")
async def export_patents_csv(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Patent))
    patents = result.scalars().all()

    headers = ["Patent Number", "Title", "Assignee", "IPC Code", "Domain", "Citation Count"]
    rows = [
        [p.patent_number, p.title, p.assignee, p.ipc_classification, p.technology_domain, p.citation_count]
        for p in patents
    ]

    csv_content = ExportService.generate_csv_report(headers, rows)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=patent_landscape_report.csv"},
    )


@reports_router.get("/patents/export/json")
async def export_patents_json(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Patent))
    patents = result.scalars().all()

    records = [
        {
            "patent_number": p.patent_number,
            "title": p.title,
            "assignee": p.assignee,
            "ipc_classification": p.ipc_classification,
            "technology_domain": p.technology_domain,
            "citation_count": p.citation_count,
        }
        for p in patents
    ]
    return JSONResponse(content={"report": "patent", "items": records})


@reports_router.get("/patents/export/pdf")
async def export_patents_pdf(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Patent).limit(20))
    patents = result.scalars().all()

    headers = ["Patent #", "Title", "Assignee", "IPC Code", "Domain"]
    rows = [
        [
            p.patent_number,
            p.title,
            p.assignee,
            p.ipc_classification,
            p.technology_domain,
        ]
        for p in patents
    ]

    pdf_bytes = build_pdf_bytes("Patent Landscape Report", headers, rows)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=patent_landscape_report.pdf"},
    )


@reports_router.get("/html-summary")
async def generate_html_summary_report(
    report_type: str = Query("funding", description="funding, patent, or trend"),
    db: AsyncSession = Depends(get_db),
):
    if report_type == "funding":
        result = await db.execute(select(FundingOpportunity).limit(10))
        grants = result.scalars().all()
        table_rows = "".join([
            f"<tr><td>{g.title}</td><td>{g.agency}</td><td>{g.currency} {g.max_award:,}</td><td><span class='badge'>{g.status}</span></td></tr>"
            for g in grants
        ])
        content = f"""
        <h2>Active Funding Opportunities & Grants Executive Briefing</h2>
        <table>
            <thead><tr><th>Title</th><th>Agency</th><th>Max Award</th><th>Status</th></tr></thead>
            <tbody>{table_rows}</tbody>
        </table>
        """
        html = ExportService.generate_printable_html_report(
            "Funding Intelligence Report",
            "Grants & Innovation Funding",
            content,
        )
    else:
        result = await db.execute(select(Patent).limit(10))
        patents = result.scalars().all()
        table_rows = "".join([
            f"<tr><td>{p.patent_number}</td><td>{p.title}</td><td>{p.assignee}</td><td>{p.ipc_classification}</td></tr>"
            for p in patents
        ])
        content = f"""
        <h2>Intellectual Property & Patent Landscape Briefing</h2>
        <table>
            <thead><tr><th>Patent #</th><th>Title</th><th>Assignee</th><th>IPC Code</th></tr></thead>
            <tbody>{table_rows}</tbody>
        </table>
        """
        html = ExportService.generate_printable_html_report(
            "Patent Landscape Report",
            "Intellectual Property Analytics",
            content,
        )

    return Response(content=html, media_type="text/html")


@reports_router.get("/generate")
async def generate_report(report_type: str = Query("funding", description="funding or patent")):
    if report_type == "funding":
        return {
            "status": "generated",
            "reportType": "funding",
            "csvUrl": "/api/v1/reports/funding/export/csv",
            "jsonUrl": "/api/v1/reports/funding/export/json",
            "pdfUrl": "/api/v1/reports/funding/export/pdf",
            "previewUrl": "/api/v1/reports/html-summary?report_type=funding",
            "message": "Funding report generated successfully.",
        }
    elif report_type == "patent":
        return {
            "status": "generated",
            "reportType": "patent",
            "csvUrl": "/api/v1/reports/patents/export/csv",
            "jsonUrl": "/api/v1/reports/patents/export/json",
            "pdfUrl": "/api/v1/reports/patents/export/pdf",
            "previewUrl": "/api/v1/reports/html-summary?report_type=patent",
            "message": "Patent landscape report generated successfully.",
        }
    return {
        "status": "error",
        "message": "Unsupported report_type. Use funding or patent.",
    }
