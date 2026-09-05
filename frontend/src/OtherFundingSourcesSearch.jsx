import { useState } from "react";
import axios from "axios";

const SOURCE_LABELS = {
  horizon: "Horizon Europe (EU)",
  ukri: "UKRI (UK)",
  anrf: "ANRF (India)",
  birac: "BIRAC (India)",
  dbt: "DBT (India)",
  icmr: "ICMR (India)",
  wellcome: "Wellcome",
};

function OtherFundingSourcesSearch({ token }) {
  const [source, setSource] = useState("horizon");
  const [keyword, setKeyword] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage("");
    try {
      const response = await axios.get(
        `http://127.0.0.1:8000/api/v1/funding/search-live-sources/${source}`,
        {
          params: { keyword },
          headers: { Authorization: "Bearer " + token },
        }
      );
      setResults(response.data);
      if (response.data.length === 0) {
        setMessage("No opportunities found for this search.");
      }
    } catch (err) {
      setMessage(err.response?.data?.detail || "Search failed. Please try again.");
    }
    setLoading(false);
  };

  return (
    <div>
      <form className="search-form" onSubmit={handleSearch} style={{ flexWrap: "wrap" }}>
        <select
          value={source}
          onChange={(e) => setSource(e.target.value)}
          style={{
            padding: "10px 12px",
            borderRadius: "6px",
            border: "1px solid #d0d7de",
            fontSize: "14px",
            marginRight: "8px",
          }}
        >
          {Object.entries(SOURCE_LABELS).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
        <input
          type="text"
          placeholder="Keyword (optional, e.g. biotechnology)"
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
        />
        <button type="submit" className="search-btn" disabled={loading}>
          {loading ? "Searching..." : "Search"}
        </button>
      </form>

      {message && <p className="dash-empty">{message}</p>}

      {results.length > 0 && (
        <div className="funding-grid">
          {results.map((item, idx) => (
            <div key={idx} className="funding-item">
              <h4>{item.title}</h4>
              <div className="funding-meta">
                <span className="funding-tag">{item.source}</span>
              </div>
              <p style={{ fontSize: "13px", color: "var(--slate)" }}>
                <strong>Deadline:</strong> {item.deadline || "See details"}
              </p>
              <p className="funding-desc">{item.description}</p>
              <a href={item.link} target="_blank" rel="noopener noreferrer" className="grants-link">
                View details
              </a>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default OtherFundingSourcesSearch;