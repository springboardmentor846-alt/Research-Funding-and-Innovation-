import { useEffect, useState } from "react";
import {
  Activity,
  CheckCircle2,
  Clock3,
  ShieldCheck,
  UserCheck,
  UserRoundX,
  Users,
} from "lucide-react";
import { getAdminOverview } from "../../api/admin";

function formatDate(value) {
  if (!value) return "—";
  return new Date(value).toLocaleString([], {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function roleLabel(role) {
  if (role === "startup_founder") return "Startup Founder";
  if (role === "administrator") return "Administrator";
  return "Researcher";
}

export default function AdminDashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const loadOverview = async () => {
    try {
      setLoading(true);
      setError("");
      setData(await getAdminOverview());
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Unable to load administrator overview."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadOverview();
  }, []);

  if (loading) {
    return (
      <div className="admin-loading">
        <div className="spinner-border text-primary" role="status" />
        <span>Loading administrator console...</span>
      </div>
    );
  }

  return (
    <div className="admin-page">
      <div className="admin-page-header">
        <div>
          <span className="admin-eyebrow">ADMINISTRATION</span>
          <h1>Platform overview</h1>
          <p>
            Monitor users, access, and the operational state of InnovFund.
          </p>
        </div>

        <div className="admin-secure-chip">
          <ShieldCheck size={15} />
          Protected administrator area
        </div>
      </div>

      {error && <div className="admin-alert error">{error}</div>}

      {data && (
        <>
          <section className="admin-stat-grid">
            <div className="admin-stat-card">
              <div className="admin-stat-icon blue"><Users size={20} /></div>
              <span>Total users</span>
              <strong>{data.total_users}</strong>
              <small>All registered accounts</small>
            </div>

            <div className="admin-stat-card">
              <div className="admin-stat-icon green"><UserCheck size={20} /></div>
              <span>Active users</span>
              <strong>{data.active_users}</strong>
              <small>Accounts currently enabled</small>
            </div>

            <div className="admin-stat-card">
              <div className="admin-stat-icon amber"><UserRoundX size={20} /></div>
              <span>Inactive users</span>
              <strong>{data.inactive_users}</strong>
              <small>Accounts currently disabled</small>
            </div>

            <div className="admin-stat-card">
              <div className="admin-stat-icon purple"><ShieldCheck size={20} /></div>
              <span>Administrators</span>
              <strong>{data.administrators}</strong>
              <small>Privileged accounts</small>
            </div>
          </section>

          <section className="admin-role-grid">
            <div className="admin-panel admin-role-panel">
              <div className="admin-panel-heading">
                <div>
                  <h2>User distribution</h2>
                  <p>Current accounts grouped by platform role.</p>
                </div>
                <Activity size={18} />
              </div>

              <div className="admin-role-list">
                <div>
                  <span>Researchers</span>
                  <strong>{data.researchers}</strong>
                </div>
                <div>
                  <span>Startup founders</span>
                  <strong>{data.startup_founders}</strong>
                </div>
                <div>
                  <span>Administrators</span>
                  <strong>{data.administrators}</strong>
                </div>
              </div>
            </div>

            <div className="admin-panel admin-session-panel">
              <div className="admin-panel-heading">
                <div>
                  <h2>Current session</h2>
                  <p>Authenticated administrator account.</p>
                </div>
                <CheckCircle2 size={18} />
              </div>

              <div className="admin-session-details">
                <strong>{data.current_admin.full_name}</strong>
                <span>{data.current_admin.email}</span>
                <span className="admin-role-badge">
                  {roleLabel(data.current_admin.role)}
                </span>
              </div>
            </div>
          </section>

          <section className="admin-panel admin-recent-panel">
            <div className="admin-panel-heading">
              <div>
                <h2>Recently registered users</h2>
                <p>Latest accounts created on the platform.</p>
              </div>
              <Clock3 size={18} />
            </div>

            <div className="admin-table-wrap">
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>User</th>
                    <th>Role</th>
                    <th>Status</th>
                    <th>Registered</th>
                  </tr>
                </thead>
                <tbody>
                  {data.recent_users.length ? (
                    data.recent_users.map((item) => (
                      <tr key={item.user_id}>
                        <td>
                          <div className="admin-user-cell">
                            <span className="admin-table-avatar">
                              {item.full_name.charAt(0).toUpperCase()}
                            </span>
                            <div>
                              <strong>{item.full_name}</strong>
                              <small>{item.email}</small>
                            </div>
                          </div>
                        </td>
                        <td>{roleLabel(item.role)}</td>
                        <td>
                          <span className={`admin-status ${item.is_active ? "active" : "inactive"}`}>
                            {item.is_active ? "Active" : "Inactive"}
                          </span>
                        </td>
                        <td>{formatDate(item.created_at)}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="4" className="admin-empty-cell">
                        No users have been registered yet.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </section>
        </>
      )}
    </div>
  );
}
