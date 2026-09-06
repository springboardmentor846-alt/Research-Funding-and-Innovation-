import { useEffect, useState } from "react";
import axios from "axios";

function _countCsv(value) {
  if (!value) return 0;
  return value.split(",").map((v) => v.trim()).filter(Boolean).length;
}

function DashboardOverview({ token, profile, onNavigate }) {
  const [stats, setStats] = useState({
    domains: 0,
    keywords: 0,
    technologyAreas: 0,
    publications: 0,
    patents: 0,
    funding: 0,
    innovation: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const authHeaders = { headers: { Authorization: `Bearer ${token}` } };

    const load = async () => {
      setLoading(true);
      try {
        const [profileRes, pubsRes, patentsRes, fundingRes, scoreRes] = await Promise.allSettled([
          axios.get("http://127.0.0.1:8000/api/v1/profile/", authHeaders),
          axios.get("http://127.0.0.1:8000/api/v1/profile/publications", authHeaders),
          axios.get("http://127.0.0.1:8000/api/v1/profile/patents", authHeaders),
          axios.get("http://127.0.0.1:8000/api/v1/funding/recommended", authHeaders),
          axios.get("http://127.0.0.1:8000/api/v1/profile/innovation-score", authHeaders),
        ]);

        const p = profileRes.status === "fulfilled" ? profileRes.value.data : null;

        setStats({
          domains: p ? _countCsv(p.research_domains) : 0,
          keywords: p ? _countCsv(p.keywords) : 0,
          technologyAreas: p ? _countCsv(p.technology_areas) : 0,
          publications: pubsRes.status === "fulfilled" ? pubsRes.value.data.length : 0,
          patents: patentsRes.status === "fulfilled" ? patentsRes.value.data.length : 0,
          funding: fundingRes.status === "fulfilled" ? fundingRes.value.data.length : 0,
          innovation: scoreRes.status === "fulfilled" ? scoreRes.value.data.innovation_score : 0,
        });
      } catch (err) {
        // Leave stats at zero defaults — the rest of the dashboard still works.
      }
      setLoading(false);
    };

    load();
  }, [token]);

  const modules = [
    {
      title: "Research Profile",
      description: "Manage your complete research profile, organization, domains, keywords and technology expertise",
      tab: "research-profile",
      icon: "RP",
    },
    {
      title: "Publications",
      description: "Add and manage journal articles, papers and research outputs.",
      tab: "research-profile",
      icon: "PB",
      count: stats.publications,
    },
    {
      title: "Patents",
      description: "Maintain patent applications and innovation records.",
      tab: "research-profile",
      icon: "PT",
      count: stats.patents,
    },
    {
      title: "Funding Opportunities",
      description: "Browse government and international funding programs.",
      tab: "funding",
      icon: "$",
      count: stats.funding,
    },
    {
      title: "Global Patent Landscape",
      description: "Analyze global patent trends and competitors.",
      tab: "patents",
      icon: "GL",
    },
    {
      title: "Innovation Score",
      description: "View your AI-generated innovation score and detailed breakdown.",
      tab: "innovation-score",
      icon: "IS",
      count: `${stats.innovation}/100`,
    },
    {
      title: "Research Trends",
      description: "Explore publication trends across research domains.",
      tab: "research-trends",
      icon: "RT",
    },
    {
      title: "Research Library",
      description: "Papers saved for reference from OpenAlex and Crossref.",
      tab: "research-library",
      icon: "RL",
    },
  ];

  return (
    <div>
      <div className="dash-card" style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: "16px" }}>
        <div>
          <span style={{ fontSize: "12px", fontWeight: 700, letterSpacing: "0.05em", color: "#1C8C7A" }}>
            RESEARCHER WORKSPACE
          </span>
          <h2 style={{ margin: "6px 0" }}>Welcome back, {profile?.name || profile?.email?.split("@")[0] || "Researcher"}</h2>
          <p className="dash-card-subtitle">
            Manage your research identity, innovation records, and profile intelligence from one workspace.
          </p>
        </div>
      </div>

      <div className="dash-card">
        <h3>Your Snapshot</h3>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "14px", marginTop: "10px" }}>
          {[
            { label: "Research Domains", value: stats.domains, hint: "Broad research fields" },
            { label: "Publications", value: stats.publications, hint: "Scholarly research outputs" },
            { label: "Patents", value: stats.patents, hint: "Intellectual property records" },
            { label: "Innovation Score", value: `${stats.innovation}/100`, hint: "AI calculated" },
          ].map((s) => (
            <div
              key={s.label}
              style={{
                flex: "1 1 160px",
                background: "#f7f9fb",
                borderRadius: "10px",
                padding: "14px 16px",
              }}
            >
              <div style={{ fontSize: "12px", color: "#667085", fontWeight: 600 }}>{s.label}</div>
              <div style={{ fontSize: "24px", fontWeight: 700, margin: "4px 0" }}>
                {loading ? "..." : s.value}
              </div>
              <div style={{ fontSize: "11.5px", color: "#98A2B3" }}>{s.hint}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="dash-card">
        <h3>Workspace Modules</h3>
        <p className="dash-card-subtitle">Jump straight into any part of your workspace</p>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))",
            gap: "12px",
            marginTop: "12px",
          }}
        >
          {modules.map((m) => (
            <div
              key={m.title}
              onClick={() => onNavigate && onNavigate(m.tab)}
              style={{
                border: "1px solid #e5e9ef",
                borderRadius: "10px",
                padding: "14px",
                cursor: "pointer",
                transition: "border-color 0.15s ease",
              }}
              onMouseEnter={(e) => (e.currentTarget.style.borderColor = "#1C8C7A")}
              onMouseLeave={(e) => (e.currentTarget.style.borderColor = "#e5e9ef")}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <span
                  style={{
                    display: "inline-block",
                    background: "#1C8C7A",
                    color: "#fff",
                    fontSize: "11px",
                    fontWeight: 700,
                    borderRadius: "6px",
                    padding: "3px 7px",
                  }}
                >
                  {m.icon}
                </span>
                {m.count !== undefined && (
                  <span style={{ fontWeight: 700, fontSize: "14px" }}>{loading ? "..." : m.count}</span>
                )}
              </div>
              <div style={{ fontWeight: 600, marginTop: "8px", fontSize: "14px" }}>{m.title}</div>
              <div style={{ fontSize: "12px", color: "#667085", marginTop: "4px" }}>{m.description}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default DashboardOverview;