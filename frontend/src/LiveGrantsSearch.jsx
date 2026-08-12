import { useState } from "react";
import axios from "axios";

function LiveGrantsSearch({ token }) {
  const [keyword, setKeyword] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!keyword.trim()) return;
    setLoading(true);
    setMessage("");
    try {
      const response = await axios.get(
        "http://127.0.0.1:8000/api/v1/funding/search-live",
        {
          params: { keyword: keyword },
          headers: { Authorization: "Bearer " + token },
        }
      );
      setResults(response.data);
      if (response.data.length === 0) {
        setMessage("No live grants found for this keyword.");
      }
    } catch (err) {
      setMessage("Search failed. Please try again.");
    }
    setLoading(false);
  };

  return (
    <div>
      <form className="search-form" onSubmit={handleSearch}>
        <input
          type="text"
          placeholder="Search real US federal grants"
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
                <strong>Deadline:</strong> {item.deadline ? item.deadline : "See details"}
              </p>
              <p className="funding-desc">{item.description}</p>
              <a href={item.link} target="_blank" rel="noopener noreferrer" className="grants-link">
                View on Grants.gov
              </a>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default LiveGrantsSearch;
