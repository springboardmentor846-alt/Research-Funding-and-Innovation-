import io
import csv
from typing import List, Dict, Any

class ReportGeneratorService:
    @staticmethod
    def generate_csv_report(title: str, headers: List[str], rows: List[List[Any]]) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([f"# {title}"])
        writer.writerow(headers)
        for row in rows:
            writer.writerow(row)
        return output.getvalue()

    @staticmethod
    def generate_summary_text(report_type: str, data_summary: Dict[str, Any]) -> str:
        return f"--- OFFICIAL PLATFORM {report_type.upper()} REPORT ---\nGenerated: {data_summary.get('generated_at')}\nTotal Records Analyzed: {data_summary.get('total_count')}\nKey Metric Digest: {data_summary.get('digest')}\nStatus: Verified Complete"

report_generator = ReportGeneratorService()
