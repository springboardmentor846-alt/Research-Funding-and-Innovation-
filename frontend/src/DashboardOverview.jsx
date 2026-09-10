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
          axios.get("https://research-platform-backend-e0sf.onrender.com/api/v1/profile/", authHeaders),
          axios.get("https://research-platform-backend-e0sf.onrender.com/api/v1/profile/publications", authHeaders),
          axios.get("https://research-platform-backend-e0sf.onrender.com/api/v1/profile/patents", authHeaders),
          axios.get("https://research-platform-backend-e0sf.onrender.com/api/v1/funding/recommended", authHeaders),
          axios.get("https://research-platform-backend-e0sf.onrender.com/api/v1/profile/innovation-score", authHeaders),
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
      accent: "accent-teal",
    },
    {
      title: "Publications",
      description: "Add and manage journal articles, papers and research outputs.",
      tab: "research-profile",
      icon: "PB",
      count: stats.publications,
      accent: "accent-teal",
    },
    {
      title: "Patents",
      description: "Maintain patent applications and innovation records.",
      tab: "research-profile",
      icon: "PT",
      count: stats.patents,
      accent: "accent-violet",
    },
    {
      title: "Funding Opportunities",
      description: "Browse government and international funding programs.",
      tab: "funding",
      icon: "$",
      count: stats.funding,
      accent: "accent-amber",
    },
    {
      title: "Global Patent Landscape",
      description: "Analyze global patent trends and competitors.",
      tab: "patents",
      icon: "GL",
      accent: "accent-violet",
    },
    {
      title: "Innovation Score",
      description: "View your AI-generated innovation score and detailed breakdown.",
      tab: "innovation-score",
      icon: "IS",
      count: `${stats.innovation}/100`,
      accent: "accent-slate",
    },
    {
      title: "Research Trends",
      description: "Explore publication trends across research domains.",
      tab: "research-trends",
      icon: "RT",
      accent: "accent-slate",
    },
    {
      title: "Research Library",
      description: "Papers saved for reference from OpenAlex and Crossref.",
      tab: "research-library",
      icon: "RL",
      accent: "accent-slate",
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
        <div className="stat-ledger">
          {[
            { label: "Research Domains", value: stats.domains, hint: "Broad research fields" },
            { label: "Publications", value: stats.publications, hint: "Scholarly research outputs" },
            { label: "Patents", value: stats.patents, hint: "Intellectual property records" },
            { label: "Innovation Score", value: `${stats.innovation}/100`, hint: "AI calculated" },
          ].map((s) => (
            <div key={s.label} className="stat-ledger-item">
              <div className="stat-ledger-label">{s.label}</div>
              <div className="stat-ledger-value">{loading ? "..." : s.value}</div>
              <div className="stat-ledger-hint">{s.hint}</div>
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
              className={`module-tile ${m.accent}`}
              onClick={() => onNavigate && onNavigate(m.tab)}
            >
              <div className="module-tile-top">
                <span className="module-tile-icon">{m.icon}</span>
                {m.count !== undefined && (
                  <span className="module-tile-count">{loading ? "..." : m.count}</span>
                )}
              </div>
              <div className="module-tile-title">{m.title}</div>
              <div className="module-tile-desc">{m.description}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default DashboardOverview;
