import { useEffect, useState, useCallback } from "react";
import axios from "axios";

function FindStartups({ token }) {
  const [query, setQuery] = useState("");
  const [startups, setStartups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [sentTo, setSentTo] = useState({});

  const authHeaders = { headers: { Authorization: `Bearer ${token}` } };

  const loadStartups = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const res = await axios.get(
        "http://127.0.0.1:8000/api/v1/startup/startups",
        { ...authHeaders, params: query ? { query } : {} }
      );
      setStartups(res.data.startups);
    } catch (err) {
      setError(err.response?.data?.detail || "Could not load startups.");
    }
    setLoading(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, query]);

  useEffect(() => {
    loadStartups();
  }, [loadStartups]);

  const handleSearch = (e) => {
    e.preventDefault();
    loadStartups();
  };

  const handleConnect = async (userId) => {
    try {
      await axios.post(
        "http://127.0.0.1:8000/api/v1/collaboration/",
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
          placeholder="Search by name, industry, or technology"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button type="submit" className="search-btn">Search</button>
      </form>

      {loading && <p className="dash-empty">Loading...</p>}
      {error && <p className="dash-error">{error}</p>}
      {!loading && startups.length === 0 && (
        <p className="dash-empty">No other startups found.</p>
      )}

      {startups.map((s) => (
        <div key={s.startup_id} className="dash-card" style={{ marginTop: "10px" }}>
          <p style={{ fontWeight: 600 }}>{s.startup_name}</p>
          <p className="dash-card-subtitle">
            {s.industry || "Industry not listed"} · {s.stage} · {s.location || "Location not listed"}
          </p>
          {s.technology_stack && (
            <p style={{ fontSize: "12.5px", color: "#555" }}>Tech: {s.technology_stack}</p>
          )}
          <button
            className="auth-submit"
            style={{ width: "auto", padding: "6px 16px", marginTop: "8px", fontSize: "13px" }}
            onClick={() => handleConnect(s.user_id)}
            disabled={sentTo[s.user_id]}
          >
            {sentTo[s.user_id] ? "Request Sent" : "Send Collaboration Request"}
          </button>
        </div>
      ))}
    </div>
  );
}

export default FindStartups;