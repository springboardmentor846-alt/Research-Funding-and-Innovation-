import { useEffect, useState, useCallback } from "react";
import axios from "axios";

function FindResearchers({ token }) {
  const [query, setQuery] = useState("");
  const [researchers, setResearchers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [sentTo, setSentTo] = useState({});

  const authHeaders = { headers: { Authorization: `Bearer ${token}` } };

  const loadResearchers = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const res = await axios.get(
        "https://research-platform-backend-e0sf.onrender.com/api/v1/startup/researchers",
        { ...authHeaders, params: query ? { query } : {} }
      );
      setResearchers(res.data.researchers);
    } catch (err) {
      setError(err.response?.data?.detail || "Could not load researchers.");
    }
    setLoading(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, query]);

  useEffect(() => {
    loadResearchers();
  }, [loadResearchers]);

  const handleSearch = (e) => {
    e.preventDefault();
    loadResearchers();
  };

  const handleConnect = async (userId) => {
    try {
      await axios.post(
        "https://research-platform-backend-e0sf.onrender.com/api/v1/collaboration/",
        { receiver_id: userId, message: "I'd like to explore a collaboration opportunity." },
        authHeaders
      );
      setSentTo((prev) => ({ ...prev, [userId]: true }));
    } catch (err) {
      setError(err.response?.data?.detail || "Could not send collaboration request.");
    }
  };

  return (
    <div>
      <form onSubmit={handleSearch} className="search-form">
        <input
          type="text"
          placeholder="Search by name, domain, or organization"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button type="submit" className="search-btn">Search</button>
      </form>

      {loading && <p className="dash-empty">Loading...</p>}
      {error && <p className="dash-error">{error}</p>}
      {!loading && researchers.length === 0 && (
        <p className="dash-empty">No researchers found.</p>
      )}

      {researchers.map((r) => (
        <div key={r.user_id} className="dash-card" style={{ marginTop: "10px" }}>
          <p style={{ fontWeight: 600 }}>{r.name}</p>
          <p className="dash-card-subtitle">{r.organization_name || "No organization listed"}</p>
          {r.research_domains && (
            <p style={{ fontSize: "12.5px", color: "#555" }}>Domains: {r.research_domains}</p>
          )}
          {r.keywords && (
            <p style={{ fontSize: "12.5px", color: "#555" }}>Keywords: {r.keywords}</p>
          )}
          <button
            className="auth-submit"
            style={{ width: "auto", padding: "6px 16px", marginTop: "8px", fontSize: "13px" }}
            onClick={() => handleConnect(r.user_id)}
            disabled={sentTo[r.user_id]}
          >
            {sentTo[r.user_id] ? "Request Sent" : "Send Collaboration Request"}
          </button>
        </div>
      ))}
    </div>
  );
}

export default FindResearchers;
