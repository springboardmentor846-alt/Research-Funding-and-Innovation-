import { useEffect, useState } from "react";
import axios from "axios";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

function TagList({ items, emptyText }) {
  if (!items || items.length === 0) {
    return <p className="dash-empty">{emptyText}</p>;
  }
  return (
    <div className="admin-role-breakdown">
      {items.map((item) => (
        <span key={item.name} className="role-badge role-researcher">
          {item.name}: {item.count}
        </span>
      ))}
    </div>
  );
}

function PlatformTrends({ token }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    setError("");
    axios
      .get("https://research-platform-backend-e0sf.onrender.com/api/v1/trends/overview", {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then((res) => setData(res.data))
      .catch(() => setError("Could not load platform trends."))
      .finally(() => setLoading(false));
  }, [token]);

  if (loading) return <p className="dash-empty">Loading platform trends...</p>;
  if (error) return <p className="dash-empty admin-error">{error}</p>;
  if (!data) return null;

  const chartData = data.publications_by_year.map((row) => ({
    year: row.year,
    count: row.count,
  }));

  return (
    <div>
      <div className="dash-card" style={{ marginBottom: "16px" }}>
        <h4 className="admin-subheading">Publications by Year (platform-wide)</h4>
        {chartData.length === 0 ? (
          <p className="dash-empty">No publications recorded yet.</p>
        ) : (
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={chartData}>
              <XAxis dataKey="year" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="count" fill="#2E5EAA" />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      <div className="dash-card" style={{ marginBottom: "16px" }}>
        <h4 className="admin-subheading">Top Research Domains</h4>
        <TagList items={data.top_domains} emptyText="No domains recorded yet." />
      </div>

      <div className="dash-card" style={{ marginBottom: "16px" }}>
        <h4 className="admin-subheading">Top Keywords</h4>
        <TagList items={data.top_keywords} emptyText="No keywords recorded yet." />
      </div>

      <div className="dash-card">
        <h4 className="admin-subheading">Top Technology Areas</h4>
        <TagList items={data.top_technology_areas} emptyText="No technology areas recorded yet." />
      </div>
    </div>
  );
}

export default PlatformTrends;
