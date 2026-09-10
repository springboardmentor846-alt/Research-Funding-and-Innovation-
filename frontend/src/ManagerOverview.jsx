import { useEffect, useState } from "react";
import axios from "axios";

function ManagerOverview({ token }) {
  const [overview, setOverview] = useState(null);
  const [startups, setStartups] = useState([]);
  const [activity, setActivity] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const headers = { Authorization: `Bearer ${token}` };
    setLoading(true);
    setError("");

    Promise.allSettled([
      axios.get("https://research-platform-backend-e0sf.onrender.com/api/v1/manager/overview", { headers }),
      axios.get("https://research-platform-backend-e0sf.onrender.com/api/v1/manager/startups", { headers }),
      axios.get("https://research-platform-backend-e0sf.onrender.com/api/v1/manager/collaboration-activity", { headers }),
    ]).then(([overviewRes, startupsRes, activityRes]) => {
      if (overviewRes.status === "fulfilled") setOverview(overviewRes.value.data);
      else setError("Could not load the ecosystem overview.");
      if (startupsRes.status === "fulfilled") setStartups(startupsRes.value.data);
      if (activityRes.status === "fulfilled") setActivity(activityRes.value.data);
      setLoading(false);
    });
  }, [token]);

  if (loading) return <p className="dash-empty">Loading ecosystem overview...</p>;
  if (error) return <p className="dash-empty admin-error">{error}</p>;
  if (!overview) return null;

  const cards = [
    { label: "Total Users", value: overview.total_users },
    { label: "Research Profiles", value: overview.total_research_profiles },
    { label: "Publications", value: overview.total_publications },
    { label: "Patents", value: overview.total_patents },
    { label: "Funding Opportunities", value: overview.total_funding_opportunities },
    { label: "Startups", value: overview.total_startups },
  ];

  return (
    <div>
      <div className="stats-strip admin-stats-strip" style={{ marginBottom: "16px" }}>
        {cards.map((c) => (
          <div className="stat-box" key={c.label}>
            <span className="stat-number">{c.value}</span>
            <span className="stat-label">{c.label}</span>
          </div>
        ))}
      </div>

      <div className="dash-card" style={{ marginBottom: "16px" }}>
        <h4 className="admin-subheading">Users by Role</h4>
        <div className="admin-role-breakdown">
          {Object.entries(overview.users_by_role).map(([role, count]) => (
            <span key={role} className={`role-badge role-${role}`}>
              {role.replace(/_/g, " ")}: {count}
            </span>
          ))}
        </div>
      </div>

      <div className="dash-card" style={{ marginBottom: "16px" }}>
        <h4 className="admin-subheading">Startups ({startups.length})</h4>
        {startups.length === 0 ? (
          <p className="dash-empty">No startup profiles yet.</p>
        ) : (
          <div className="admin-table-wrap">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Industry</th>
                  <th>Stage</th>
                  <th>Funding Stage</th>
                  <th>Founder</th>
                </tr>
              </thead>
              <tbody>
                {startups.map((s) => (
                  <tr key={s.id}>
                    <td>{s.startup_name || "—"}</td>
                    <td>{s.industry || "—"}</td>
                    <td>{s.stage || "—"}</td>
                    <td>{s.funding_stage || "—"}</td>
                    <td>{s.founder_email || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="dash-card">
        <h4 className="admin-subheading">Recent Collaboration Activity</h4>
        {activity.length === 0 ? (
          <p className="dash-empty">No collaboration requests yet.</p>
        ) : (
          <div className="admin-table-wrap">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>From</th>
                  <th>To</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {activity.map((a) => (
                  <tr key={a.id}>
                    <td>{a.sender_email || "—"}</td>
                    <td>{a.receiver_email || "—"}</td>
                    <td>
                      <span className={`role-badge role-${a.status}`}>{a.status}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default ManagerOverview;
