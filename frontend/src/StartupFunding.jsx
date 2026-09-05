import { useEffect, useState, useCallback } from "react";
import axios from "axios";

function StartupPredictButton({ token, fundingId }) {
  const [open, setOpen] = useState(false);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleClick = async () => {
    if (open) {
      setOpen(false);
      return;
    }
    setOpen(true);
    if (prediction || loading) return;

    setLoading(true);
    setError("");
    try {
      const res = await axios.get(
        `http://127.0.0.1:8000/api/v1/startup/predict-success/${fundingId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setPrediction(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Could not load prediction.");
    }
    setLoading(false);
  };

  return (
    <div style={{ marginTop: "6px" }}>
      <button
        type="button"
        onClick={handleClick}
        style={{ background: "none", border: "none", color: "#2E5EAA", fontSize: "12.5px", fontWeight: 600, cursor: "pointer", padding: 0 }}
      >
        {open ? "Hide prediction" : "Predict Success"}
      </button>

      {open && (
        <div style={{ marginTop: "6px", fontSize: "12.5px" }}>
          {loading && <p className="dash-empty">Predicting...</p>}
          {error && <p className="dash-error">{error}</p>}
          {prediction && (
            <div>
              <p style={{ fontWeight: 700, color: "#1C8C7A" }}>
                {prediction.success_estimate}% estimated fit
              </p>
              <p style={{ color: "#555" }}>
                Match: {prediction.match_score}% · Readiness: {prediction.readiness_score}% · Profile completion: {prediction.profile_completion}%
              </p>
              {prediction.strengths?.length > 0 && (
                <ul style={{ margin: "6px 0", paddingLeft: "16px" }}>
                  {prediction.strengths.map((s, idx) => (
                    <li key={idx} style={{ color: "#1C8C7A" }}>{s}</li>
                  ))}
                </ul>
              )}
              {prediction.improvements?.length > 0 && (
                <ul style={{ margin: "6px 0", paddingLeft: "16px" }}>
                  {prediction.improvements.map((s, idx) => (
                    <li key={idx} style={{ color: "#B0479B" }}>{s}</li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function StartupFunding({ token }) {
  const [query, setQuery] = useState("");
  const [opportunities, setOpportunities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const res = await axios.get(
        "http://127.0.0.1:8000/api/v1/startup/funding",
        {
          headers: { Authorization: `Bearer ${token}` },
          params: query ? { query } : {},
        }
      );
      setOpportunities(res.data.funding_opportunities);
    } catch (err) {
      setError(err.response?.data?.detail || "Could not load funding opportunities.");
    }
    setLoading(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, query]);

  useEffect(() => {
    load();
  }, [load]);

  const handleSearch = (e) => {
    e.preventDefault();
    load();
  };

  return (
    <div>
      <form onSubmit={handleSearch} className="search-form">
        <input
          type="text"
          placeholder="Search funding (defaults to your startup's industry/tech)"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button type="submit" className="search-btn">Search</button>
      </form>

      {loading && <p className="dash-empty">Loading...</p>}
      {error && <p className="dash-error">{error}</p>}
      {!loading && opportunities.length === 0 && (
        <p className="dash-empty">No matching funding opportunities found.</p>
      )}

      {opportunities.map((f) => (
        <div key={f.id} className="dash-card" style={{ marginTop: "10px" }}>
          <p style={{ fontWeight: 600 }}>{f.title}</p>
          <p className="dash-card-subtitle">
            {f.source || "Unknown source"} {f.amount ? `· ${f.amount}` : ""} {f.deadline ? `· Deadline: ${f.deadline}` : ""}
          </p>
          {f.description && <p style={{ fontSize: "13px", color: "#555" }}>{f.description}</p>}
          <StartupPredictButton token={token} fundingId={f.id} />
        </div>
      ))}
    </div>
  );
}

export default StartupFunding;