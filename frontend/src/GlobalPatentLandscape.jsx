import { useState } from "react";
import axios from "axios";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

function GlobalPatentLandscape({ token }) {
  const [query, setQuery] = useState("");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError("");
    setData(null);
    try {
      const response = await axios.get(
        "http://127.0.0.1:8000/api/v1/profile/patent-landscape",
        {
          params: { query },
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      setData(response.data);
    } catch (err) {
      if (err.response?.status === 503) {
        setError("Global Patent Landscape isn't configured yet — a LENS_API_KEY is needed on the server.");
      } else {
        setError(err.response?.data?.detail || "Search failed. Please try again.");
      }
    }
    setLoading(false);
  };

  const countryChartData = data?.country_distribution?.map((c) => ({
    name: c.code,
    count: c.count,
  })) || [];

  const cpcChartData = data
    ? Object.entries(data.technology_classes || {}).map(([cpc, count]) => ({ name: cpc, count }))
    : [];

  return (
    <div>
      <form className="search-form" onSubmit={handleSearch}>
        <input
          type="text"
          placeholder="Search global patents (e.g. battery cooling, gene editing)"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button type="submit" className="search-btn" disabled={loading}>
          {loading ? "Searching..." : "Search"}
        </button>
      </form>

      {error && <p className="dash-error" style={{ marginTop: "10px" }}>{error}</p>}

      {data && (
        <div style={{ marginTop: "16px" }}>
          <p className="dash-card-subtitle">
            {data.summary.total_patents} patents · {data.summary.countries} countries ·{" "}
            {data.summary.organizations} organizations · {data.summary.technology_classes} technology classes
          </p>

          {data.personalized_relevance && (
            <p className="dash-card-subtitle" style={{ color: "#1C8C7A" }}>
              Results are ranked by relevance to your research profile.
            </p>
          )}

          {data.insights?.length > 0 && (
            <ul style={{ margin: "10px 0", paddingLeft: "18px", fontSize: "13px", color: "#555" }}>
              {data.insights.map((insight, idx) => (
                <li key={idx}>{insight}</li>
              ))}
            </ul>
          )}

          {countryChartData.length > 0 && (
            <div style={{ marginTop: "18px" }}>
              <h4 style={{ marginBottom: "8px" }}>Country Distribution</h4>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={countryChartData}>
                  <XAxis dataKey="name" />
                  <YAxis allowDecimals={false} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#1C8C7A" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {cpcChartData.length > 0 && (
            <div style={{ marginTop: "18px" }}>
              <h4 style={{ marginBottom: "8px" }}>Top CPC Technology Classes</h4>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={cpcChartData}>
                  <XAxis dataKey="name" />
                  <YAxis allowDecimals={false} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#2E5EAA" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {data.relevant_patents?.length > 0 && (
            <div style={{ marginTop: "18px" }}>
              <h4 style={{ marginBottom: "8px" }}>Top Matching Patents</h4>
              {data.relevant_patents.slice(0, 10).map((p, idx) => (
                <div key={idx} className="dash-card" style={{ marginTop: "8px" }}>
                  <p style={{ fontWeight: 600 }}>{p.title}</p>
                  <p className="dash-card-subtitle">
                    {p.jurisdiction_name || "Unknown jurisdiction"}
                    {p.applicants?.length > 0 ? ` · ${p.applicants.join(", ")}` : ""}
                    {p.publication_date ? ` · ${p.publication_date}` : ""}
                  </p>
                  {data.personalized_relevance && (
                    <p style={{ fontSize: "12px", color: "#1C8C7A" }}>
                      Relevance: {p.relevance_score}%
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default GlobalPatentLandscape;