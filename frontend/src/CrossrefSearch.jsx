import { useState } from "react";
import axios from "axios";

function CrossrefSearch({ token, onAdded }) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setMessage("");
    try {
      const response = await axios.get(
        "http://127.0.0.1:8000/api/v1/profile/crossref/search",
        {
          params: { query },
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      setResults(response.data);
      if (response.data.length === 0) {
        setMessage("No results found. Try a different search term.");
      }
    } catch (err) {
      setMessage("Search failed. Please try again.");
    }
    setLoading(false);
  };

  const handleAdd = async (pub) => {
    try {
      await axios.post(
        "http://127.0.0.1:8000/api/v1/profile/library",
        pub,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setMessage(`Saved to Research Library: ${pub.title.slice(0, 50)}...`);
      onAdded();
    } catch (err) {
      setMessage(err.response?.data?.detail || "Could not save publication.");
    }
  };

  return (
    <div>
      <form className="search-form" onSubmit={handleSearch}>
        <input
          type="text"
          placeholder="Search Crossref (e.g. graphene, CRISPR)"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button type="submit" className="search-btn" disabled={loading}>
          {loading ? "Searching..." : "Search"}
        </button>
      </form>

      {message && <p className="dash-empty" style={{ marginTop: "10px" }}>{message}</p>}

      {results.length > 0 && (
        <div className="search-results">
          {results.map((pub, idx) => (
            <div key={idx} className="search-result-item">
              <div style={{ flex: 1 }}>
                <p className="search-result-title">{pub.title}</p>
                <p className="search-result-meta">{pub.authors} · {pub.year} · {pub.source}</p>
              </div>
              <button className="search-add-btn" onClick={() => handleAdd(pub)}>
                Save to Library
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default CrossrefSearch;