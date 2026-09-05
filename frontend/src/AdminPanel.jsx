import { useEffect, useState, useCallback } from "react";
import axios from "axios";

const ALLOWED_ROLES = ["researcher", "startup_founder", "innovation_manager", "admin"];

function AdminPanel({ token, view }) {
  const [users, setUsers] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [actionMessage, setActionMessage] = useState("");

  const headers = { Authorization: `Bearer ${token}` };

  const loadUsers = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const res = await axios.get("http://127.0.0.1:8000/api/v1/admin/users", {
        headers,
        params: search ? { search } : {},
      });
      setUsers(res.data);
    } catch (err) {
      setError("Could not load users.");
    }
    setLoading(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, search]);

  useEffect(() => {
    setLoading(true);
    setError("");

    if (view === "users") {
      loadUsers();
    }

    if (view === "stats") {
      axios
        .get("http://127.0.0.1:8000/api/v1/admin/stats", { headers })
        .then((res) => setStats(res.data))
        .catch(() => setError("Could not load platform stats."))
        .finally(() => setLoading(false));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, view]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    loadUsers();
  };

  const handleRoleChange = async (userId, newRole) => {
    setActionMessage("");
    try {
      await axios.patch(
        `http://127.0.0.1:8000/api/v1/admin/users/${userId}/role`,
        { role: newRole },
        { headers }
      );
      setActionMessage(`Role updated.`);
      loadUsers();
    } catch (err) {
      setActionMessage(err.response?.data?.detail || "Could not update role.");
    }
  };

  const handleDelete = async (userId) => {
    setActionMessage("");
    try {
      await axios.delete(`http://127.0.0.1:8000/api/v1/admin/users/${userId}`, { headers });
      setActionMessage("User deleted.");
      loadUsers();
    } catch (err) {
      setActionMessage(err.response?.data?.detail || "Could not delete user.");
    }
  };

  if (error) return <p className="dash-empty admin-error">{error}</p>;

  if (view === "users") {
    return (
      <div>
        <form onSubmit={handleSearchSubmit} className="search-form" style={{ marginBottom: "12px" }}>
          <input
            type="text"
            placeholder="Search by name or email"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <button type="submit" className="search-btn">Search</button>
        </form>

        {actionMessage && <p className="dash-card-subtitle">{actionMessage}</p>}

        {loading && <p className="dash-empty">Loading users...</p>}
        {!loading && users.length === 0 && <p className="dash-empty">No users found.</p>}

        {!loading && users.length > 0 && (
          <div className="admin-table-wrap">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id}>
                    <td className="admin-table-id">{u.id}</td>
                    <td>{u.name || "—"}</td>
                    <td>{u.email}</td>
                    <td>
                      <select
                        value={u.role}
                        onChange={(e) => handleRoleChange(u.id, e.target.value)}
                        style={{ padding: "4px 8px", borderRadius: "6px", fontSize: "12.5px" }}
                      >
                        {ALLOWED_ROLES.map((role) => (
                          <option key={role} value={role}>
                            {role.replace(/_/g, " ")}
                          </option>
                        ))}
                      </select>
                    </td>
                    <td>
                      <button
                        onClick={() => handleDelete(u.id)}
                        style={{
                          background: "none",
                          border: "none",
                          color: "#B0479B",
                          fontWeight: 600,
                          fontSize: "12.5px",
                          cursor: "pointer",
                        }}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
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