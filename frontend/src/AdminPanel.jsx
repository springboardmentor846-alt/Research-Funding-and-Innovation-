import { useEffect, useState } from "react";
import axios from "axios";

function AdminPanel({ token, view }) {
  const [users, setUsers] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    setError("");
    const headers = { Authorization: `Bearer ${token}` };

    if (view === "users") {
      axios
        .get("http://127.0.0.1:8000/api/v1/admin/users", { headers })
        .then((res) => setUsers(res.data))
        .catch(() => setError("Could not load users."))
        .finally(() => setLoading(false));
    }

    if (view === "stats") {
      axios
        .get("http://127.0.0.1:8000/api/v1/admin/stats", { headers })
        .then((res) => setStats(res.data))
        .catch(() => setError("Could not load platform stats."))
        .finally(() => setLoading(false));
    }
  }, [token, view]);

  if (error) return <p className="dash-empty admin-error">{error}</p>;

  if (view === "users") {
    if (loading) return <p className="dash-empty">Loading users...</p>;
    if (users.length === 0) return <p className="dash-empty">No users found.</p>;

    return (
      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Email</th>
              <th>Role</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id}>
                <td className="admin-table-id">{u.id}</td>
                <td>{u.name || "—"}</td>
                <td>{u.email}</td>
                <td>
                  <span className={`role-badge role-${u.role}`}>
                    {u.role.replace(/_/g, " ")}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  if (view === "stats") {
    if (loading) return <p className="dash-empty">Loading platform stats...</p>;
    if (!stats) return <p className="dash-empty">No stats available.</p>;

    const cards = [
      { label: "Total Users", value: stats.total_users },
      { label: "Research Profiles", value: stats.total_profiles },
      { label: "Publications", value: stats.total_publications },
      { label: "Patents", value: stats.total_patents },
      { label: "Funding Opportunities", value: stats.total_funding_opportunities },
    ];

    return (
      <div>
        <div className="stats-strip admin-stats-strip">
          {cards.map((c) => (
            <div className="stat-box" key={c.label}>
              <span className="stat-number">{c.value}</span>
              <span className="stat-label">{c.label}</span>
            </div>
          ))}
        </div>

        <h4 className="admin-subheading">Users by Role</h4>
        <div className="admin-role-breakdown">
          {Object.entries(stats.users_by_role).map(([role, count]) => (
            <span key={role} className={`role-badge role-${role}`}>
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