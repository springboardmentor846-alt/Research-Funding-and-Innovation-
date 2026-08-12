import { useEffect, useState } from "react";
import axios from "axios";

function InnovationScore({ token }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchScore = async () => {
      try {
        const response = await axios.get(
          "http://127.0.0.1:8000/api/v1/profile/innovation-score",
          { headers: { Authorization: `Bearer ${token}` } }
        );
        setData(response.data);
      } catch (err) {
        if (err.response && err.response.status === 404) {
          setError("Create your research profile to see your innovation score.");
        } else {
          setError("Could not load innovation score.");
        }
      }
    };

    fetchScore();
  }, [token]);

  if (error) return <p className="dash-empty">{error}</p>;
  if (!data) return <p className="dash-empty">Loading...</p>;

  const labels = {
    research_novelty: "Research Novelty",
    patent_strength: "Patent Strength",
    technology_maturity: "Technology Maturity",
    market_potential: "Market Potential",
    funding_relevance: "Funding Relevance",
  };

  return (
    <div>
      <div className="score-hero">
        <div className="score-circle">
          <span className="score-number">{data.innovation_score}</span>
          <span className="score-max">/100</span>
        </div>
        <span className={`rating-badge ${data.rating.toLowerCase().replace(" ", "-")}`}>
          {data.rating}
        </span>
      </div>

      <div className="score-breakdown">
        {Object.entries(data.breakdown).map(([key, val]) => (
          <div key={key} className="score-row">
            <span className="score-label">{labels[key]} ({val.weight})</span>
            <div className="score-bar-track">
              <div className="score-bar-fill" style={{ width: `${val.score}%` }} />
            </div>
            <span className="score-value">{val.score}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default InnovationScore;
