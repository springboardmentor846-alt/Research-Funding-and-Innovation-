import { useEffect, useState, useCallback } from "react";
import axios from "axios";

const API_BASE = "https://research-platform-backend-e0sf.onrender.com/api/v1/profile";

function EntityChipList({ token, label, endpoint, placeholder }) {
  const [items, setItems] = useState([]);
  const [input, setInput] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const authHeaders = { headers: { Authorization: `Bearer ${token}` } };

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/${endpoint}`, authHeaders);
      setItems(res.data);
      setError("");
    } catch (err) {
      setError(err.response?.data?.detail || `Could not load ${label.toLowerCase()}.`);
    }
    setLoading(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, endpoint]);

  useEffect(() => {
    load();
  }, [load]);

  const handleAdd = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    try {
      await axios.post(`${API_BASE}/${endpoint}`, { name: input.trim() }, authHeaders);
      setInput("");
      setError("");
      load();
    } catch (err) {
      setError(err.response?.data?.detail || "Could not add.");
    }
  };

  const handleRemove = async (id) => {
    try {
      await axios.delete(`${API_BASE}/${endpoint}/${id}`, authHeaders);
      load();
    } catch (err) {
      setError(err.response?.data?.detail || "Could not remove.");
    }
  };

  return (
    <div style={{ marginBottom: "20px" }}>
      <label style={{ fontSize: "13px", fontWeight: 600, marginBottom: "6px", display: "block" }}>
        {label}
      </label>

      <form onSubmit={handleAdd} style={{ display: "flex", gap: "8px", marginBottom: "8px" }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={placeholder}
          style={{ flex: 1, padding: "8px 10px", border: "1px solid #d0d7de", borderRadius: "6px", fontSize: "13px" }}
        />
        <button type="submit" className="auth-submit" style={{ width: "auto", padding: "6px 16px", fontSize: "13px" }}>
          Add
        </button>
      </form>

      {error && <p className="dash-error" style={{ fontSize: "12px" }}>{error}</p>}
      {loading && <p className="dash-empty" style={{ fontSize: "12px" }}>Loading...</p>}

      <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
        {items.map((item) => (
          <span
            key={item.id}
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "6px",
              background: "#eef2f6",
              borderRadius: "14px",
              padding: "4px 10px",
              fontSize: "12.5px",
            }}
          >
            {item.name}
            <span
              onClick={() => handleRemove(item.id)}
              style={{ cursor: "pointer", color: "#B0479B", fontWeight: 700 }}
            >
              ×
            </span>
          </span>
        ))}
      </div>
    </div>
  );
}

function ProfileEntitiesManager({ token }) {
  return (
    <div className="dash-card">
      <h3>Research Domains, Keywords &amp; Technology Areas</h3>
      <p className="dash-card-subtitle" style={{ marginBottom: "16px" }}>
        Manage these individually — they stay in sync with the fields above.
      </p>

      <div id="profile-domains-section">
        <EntityChipList
          token={token}
          label="Research Domains"
          endpoint="domains"
          placeholder="e.g. Artificial Intelligence"
        />
      </div>
      <div id="profile-keywords-section">
        <EntityChipList
          token={token}
          label="Keywords"
          endpoint="keywords"
          placeholder="e.g. deep learning"
        />
      </div>
      <div id="profile-tech-areas-section">
        <EntityChipList
          token={token}
          label="Technology Areas"
          endpoint="technology-areas"
          placeholder="e.g. Neural Networks"
        />
      </div>
    </div>
  );
}

export default ProfileEntitiesManager;
