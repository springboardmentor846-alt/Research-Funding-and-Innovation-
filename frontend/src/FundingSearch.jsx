import { useState } from "react";
import axios from "axios";

function FundingSearch() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [searched, setSearched] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.get("http://127.0.0.1:8000/api/v1/funding/search", {
        params: { query },
      });
      setResults(response.data);
      setSearched(true);
    } catch (err) {
      setResults([]);
      setSearched(true);
    }
  };

  return (
    <div>
      <form className="search-form" onSubmit={handleSearch}>
        <input
          type="text"
          placeholder="Search funding by keyword (e.g. AI, healthcare, blockchain)"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button type="submit" className="search-btn">Search</button>
      </form>

      {searched && results.length === 0 && (
        <p className="dash-empty" style={{ marginTop: "12px" }}>No funding opportunities found.</p>
      )}

      {results.length > 0 && (
        <div className="funding-grid" style={{ marginTop: "16px" }}>
          {results.map((item) => (
            <div key={item.id} className="funding-item">
              <h4>{item.title}</h4>
              <div className="funding-meta">
                <span className="funding-tag">{item.source}</span>
                <span className="funding-amount">{item.amount}</span>
              </div>
              <p style={{ fontSize: "13px", color: "var(--slate)" }}>
                <strong>Deadline:</strong> {item.deadline}
              </p>
              <p className="funding-desc">{item.description}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default FundingSearch;
