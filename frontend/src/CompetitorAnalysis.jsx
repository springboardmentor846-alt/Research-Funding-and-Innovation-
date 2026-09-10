import { useEffect, useState } from "react";
import axios from "axios";

function CompetitorAnalysis() {
  const [competitors, setCompetitors] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchCompetitors = async () => {
      try {
        const response = await axios.get(
          "https://research-platform-backend-e0sf.onrender.com/api/v1/profile/patents/competitor-analysis"
        );
        setCompetitors(response.data);
      } catch (err) {
        setError("Could not load competitor analysis");
      }
    };

    fetchCompetitors();
  }, []);

  if (error) return <p className="dash-error">{error}</p>;

  if (competitors.length === 0) {
    return <p className="dash-empty">No patent data yet.</p>;
  }

  const maxCount = Math.max(...competitors.map((c) => c.patent_count));

  return (
    <div className="hotspot-list">
      {competitors.map((c) => (
        <div key={c.assignee} className="hotspot-row">
          <span className="hotspot-name" style={{ textTransform: "none" }}>
            {c.assignee}
          </span>
          <div className="hotspot-bar-track">
            <div
              className="hotspot-bar-fill"
              style={{ width: `${(c.patent_count / maxCount) * 100}%` }}
            />
          </div>
          <span className="hotspot-count">{c.patent_count}</span>
        </div>
      ))}
    </div>
  );
}

export default CompetitorAnalysis;

