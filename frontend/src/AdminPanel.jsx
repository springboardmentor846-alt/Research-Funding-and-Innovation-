import { useEffect, useState } from "react";
import axios from "axios";

function AdminPanel({ token, view }) {
  const [users, setUsers] = useState([]);
  const [stats, setStats] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const headers = { Authorization: `Bearer ${token}` };

    if (view === "users") {
      axios
        .get("http://127.0.0.1:8000/api/admin/users", { headers })
        .then((res) => setUsers(res.data))
        .catch(() => setError("Could not load users."));
    }

    if (view === "stats") {
      axios
        .get("http://127.0.0.1:8000/api/admin/stats", { headers })
        .then((res) => setStats(res.data))
        .catch(() => setError("Could not load platform stats."));
    }
  }, [token, view]);

  if (error) return <p className="dash-empty">{error}</p>;

  if (view === "users") {
    if (users.length === 0) return <p className="dash-empty">Loading users...</p>;
    return (
      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ textAlign: "left", borderBottom: "1px solid var(--border-light)" }}>
              <th style={{ padding: "10px 8px", fontSize: "12.5px", color: "var(--slate)" }}>ID</th>
              <th style={{ padding: "10px 8px", fontSize: "12.5px", color: "var(--slate)" }}>Name</th>
              <th style={{ padding: "10px 8px", fontSize: "12.5px", color: "var(--slate)" }}>Email</th>
              <th style={{ padding: "10px 8px", fontSize: "12.5px", color: "var(--slate)" }}>Role</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id} style={{ borderBottom: "1px solid var(--border-light)" }}>
                <td style={{ padding: "10px 8px", fontSize: "13px" }}>{u.id}</td>
                <td style={{ padding: "10px 8px", fontSize: "13px" }}>{u.name || "—"}</td>
                <td style={{ padding: "10px 8px", fontSize: "13px" }}>{u.email}</td>
                <td style={{ padding: "10px 8px", fontSize: "13px" }}>
                  <span className="funding-tag">{u.role}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  if (view === "stats") {
    if (!stats) return <p className="dash-empty">Loading platform stats...</p>;
    const cards = [
      { label: "Total Users", value: stats.total_users },
      { label: "Research Profiles", value: stats.total_profiles },
      { label: "Publications", value: stats.total_publications },
      { label: "Patents", value: stats.total_patents },
      { label: "Funding Opportunities", value: stats.total_funding_opportunities },
    ];
    return (
      <div>
        <div className="stats-strip" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))" }}>
          {cards.map((c) => (
            <div className="stat-box" key={c.label}>
              <span className="stat-number">{c.value}</span>
              <span className="stat-label">{c.label}</span>
            </div>
          ))}
        </div>

        <h4 style={{ marginTop: "20px", marginBottom: "10px" }}>Users by Role</h4>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "10px" }}>
          {Object.entries(stats.users_by_role).map(([role, count]) => (
            <span key={role} className="funding-tag" style={{ fontSize: "13px", padding: "6px 12px" }}>
              {role.replace(/_/g, " ")}: {count}
            </span>
          ))}
        </div>
      </div>
    );
  }

  return null;
}

export default AdminPanel;