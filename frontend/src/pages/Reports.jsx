import { useState } from "react";
import api from "../api/api";
import { toast } from "react-toastify";

import "./Reports.css";

export default function Reports() {
  const [loading, setLoading] = useState("");

  const reports = [
    {
      type: "funding",
      title: "Funding Report",
      description:
        "Export funding opportunities and their key details.",
      icon: "cash-coin",
    },
    {
      type: "patents",
      title: "Patent Report",
      description:
        "Export your patent portfolio and technology information.",
      icon: "lightbulb",
    },
    {
      type: "research-trends",
      title: "Research Trend Report",
      description:
        "Export publication trends grouped by research year.",
      icon: "bar-chart-line",
    },
    {
      type: "innovation",
      title: "Innovation Intelligence Report",
      description:
        "Export innovation metrics and the calculated innovation score.",
      icon: "award",
    },
    {
      type: "commercialization",
      title: "Commercialization Report",
      description:
        "Export commercialization recommendations based on your portfolio.",
      icon: "building",
    },
  ];

  const downloadReport = async (type, format) => {
    const key = `${type}-${format}`;

    try {
      setLoading(key);

      const response = await api.get(
        `/reports/${type}/${format}`,
        {
          responseType: "blob",
        }
      );

      const blob = new Blob(
        [response.data],
        {
          type:
            format === "pdf"
              ? "application/pdf"
              : "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }
      );

      const url = window.URL.createObjectURL(blob);

      const link = document.createElement("a");

      link.href = url;

      link.download = `${type}-report.${format === "excel" ? "xlsx" : "pdf"}`;

      document.body.appendChild(link);

      link.click();

      link.remove();

      window.URL.revokeObjectURL(url);

      toast.success(
        `${format.toUpperCase()} report generated successfully`
      );
    } catch (error) {
      console.error(error);

      toast.error(
        `Unable to generate ${format.toUpperCase()} report`
      );
    } finally {
      setLoading("");
    }
  };

  return (
    <section className="reports-page">

      <div className="page-heading">

        <div>

          <p className="eyebrow">
            REPORTS & EXPORT
          </p>

          <h1>
            Research Reports
          </h1>

          <p>
            Generate reports from your research,
            innovation, patent and funding data.
          </p>

        </div>

      </div>


      <div className="reports-grid">

        {reports.map((report) => (

          <article
            className="report-card"
            key={report.type}
          >

            <div className="report-icon">

              <i
                className={`bi bi-${report.icon}`}
              ></i>

            </div>


            <div className="report-content">

              <h2>
                {report.title}
              </h2>

              <p>
                {report.description}
              </p>

            </div>


            <div className="report-actions">

              <button
                type="button"
                className="report-button report-pdf"
                disabled={
                  loading === `${report.type}-pdf`
                }
                onClick={() =>
                  downloadReport(
                    report.type,
                    "pdf"
                  )
                }
              >

                <i className="bi bi-file-earmark-pdf"></i>

                {loading === `${report.type}-pdf`
                  ? "Generating..."
                  : "PDF"}

              </button>


              <button
                type="button"
                className="report-button report-excel"
                disabled={
                  loading === `${report.type}-excel`
                }
                onClick={() =>
                  downloadReport(
                    report.type,
                    "excel"
                  )
                }
              >

                <i className="bi bi-file-earmark-spreadsheet"></i>

                {loading === `${report.type}-excel`
                  ? "Generating..."
                  : "Excel"}

              </button>

            </div>

          </article>

        ))}

      </div>

    </section>
  );
}