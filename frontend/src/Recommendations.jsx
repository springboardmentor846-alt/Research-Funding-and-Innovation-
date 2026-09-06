import { useEffect, useState } from "react";
import axios from "axios";

function scorePercent(score) {
  return `${Math.round(score * 100)}%`;
}

function Recommendations({ token }) {
  const [funding, setFunding] = useState([]);
  const [collaborators, setCollaborators] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const headers = { Authorization: `Bearer ${token}` };
    setLoading(true);
    setError("");

    Promise.allSettled([
      axios.get("http://127.0.0.1:8000/api/v1/recommendations/funding", { headers }),
      axios.get("http://127.0.0.1:8000/api/v1/recommendations/collaborators", { headers }),
    ]).then(([fundingRes, collabRes]) => {
      if (fundingRes.status === "fulfilled") {
        setFunding(fundingRes.value.data);
      } else if (fundingRes.reason?.response?.status === 404) {
        setError(fundingRes.reason.response.data.detail);
      }
      if (collabRes.status === "fulfilled") {
        setCollaborators(collabRes.value.data);
      }
      setLoading(false);
    });
  }, [token]);

  if (loading) return <p className="dash-empty">Finding your best matches...</p>;
  if (error) return <p className="dash-empty">{error}</p>;

  return (
    <div>
      <div className="dash-card" style={{ marginBottom: "16px" }}>
        <h4 className="admin-subheading">Recommended Funding Opportunities</h4>
        {funding.length === 0 ? (
          <p className="dash-empty">No close matches found yet — add more domains and keywords to your profile.</p>
        ) : (
          <div className="admin-table-wrap">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Source</th>
                  <th>Deadline</th>
                  <th>Amount</th>
                  <th>Match</th>
                </tr>
              </thead>
              <tbody>
                {funding.map((f) => (
                  <tr key={f.id}>
                    <td>
                      {f.link ? (
                        <a href={f.link} target="_blank" rel="noreferrer">{f.title}</a>
                      ) : (
                        f.title
                      )}
                    </td>
                    <td>{f.source || "—"}</td>
                    <td>{f.deadline || "—"}</td>
                    <td>{f.amount || "—"}</td>
                    <td>{scorePercent(f.match_score)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="dash-card">
        <h4 className="admin-subheading">Recommended Collaborators</h4>
        {collaborators.length === 0 ? (
          <p className="dash-empty">No close matches found yet.</p>
        ) : (
          <div className="admin-table-wrap">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Organization</th>
                  <th>Research Domains</th>
                  <th>Match</th>
                </tr>
              </thead>
              <tbody>
                {collaborators.map((c) => (
                  <tr key={c.user_id}>
                    <td>{c.name || "—"}</td>
                    <td>{c.organization_name || "—"}</td>
                    <td>{c.research_domains || "—"}</td>
                    <td>{scorePercent(c.match_score)}</td>
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

export default Recommendations;