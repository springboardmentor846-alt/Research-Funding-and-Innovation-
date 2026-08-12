import { useState } from "react";
import axios from "axios";

function Reports({ token }) {
  const [downloading, setDownloading] = useState("");
  const [message, setMessage] = useState("");

  const downloadFile = async (type) => {
    setDownloading(type);
    setMessage("");
    try {
      const endpoint =
        type === "pdf"
          ? "http://127.0.0.1:8000/api/profile/reports/pdf"
          : "http://127.0.0.1:8000/api/profile/reports/excel";

      const response = await axios.get(endpoint, {
        headers: { Authorization: `Bearer ${token}` },
        responseType: "blob",
      });

      const filename = type === "pdf" ? "innovation_report.pdf" : "innovation_report.xlsx";
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setMessage(
        "Could not generate report. Make sure your research profile is created first."
      );
    }
    setDownloading("");
  };

  const cardStyle = {
    border: "1px solid var(--border-light)",
    borderRadius: "10px",
    padding: "20px",
    display: "flex",
    flexDirection: "column",
    gap: "10px",
    background: "var(--paper)",
  };

  const btnStyle = {
    background: "#1C8C7A",
    color: "#fff",
    border: "none",
    padding: "10px 18px",
    borderRadius: "8px",
    fontSize: "13.5px",
    fontWeight: 600,
    cursor: "pointer",
    alignSelf: "flex-start",
  };

  return (
    <div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "16px" }}>
        <div style={cardStyle}>
          <h4 style={{ margin: 0 }}>📄 PDF Report</h4>
          <p style={{ fontSize: "13px", color: "var(--slate)", margin: 0 }}>
            A full innovation intelligence summary — profile, innovation score
            breakdown, publications, patents, funding matches, and
            commercialization recommendations.
          </p>
          <button
            style={btnStyle}
            onClick={() => downloadFile("pdf")}
            disabled={downloading === "pdf"}
          >
            {downloading === "pdf" ? "Generating..." : "Download PDF"}
          </button>
        </div>

        <div style={cardStyle}>
          <h4 style={{ margin: 0 }}>📊 Excel Report</h4>
          <p style={{ fontSize: "13px", color: "var(--slate)", margin: 0 }}>
            Raw data across four sheets — Summary, Publications, Patents, and
            Funding Matches — ready for further analysis.
          </p>
          <button
            style={btnStyle}
            onClick={() => downloadFile("excel")}
            disabled={downloading === "excel"}
          >
            {downloading === "excel" ? "Generating..." : "Download Excel"}
          </button>
        </div>
      </div>

      {message && (
        <p className="dash-empty" style={{ marginTop: "14px" }}>
          {message}
        </p>
      )}
    </div>
  );
}

export default Reports;