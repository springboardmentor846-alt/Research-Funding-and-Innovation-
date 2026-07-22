import { useEffect, useState } from "react";
import { Link, useOutletContext } from "react-router-dom";
import api from "../api/axios";
import { getDashboard } from "../api/dashboard";

function Dashboard() {
  const { user } = useOutletContext();

  const [stats, setStats] = useState({
  domains: 0,
  keywords: 0,
  technologyAreas: 0,
  publications: 0,
  patents: 0,
  funding: 0,
  innovation: 0,
});

const [dashboard, setDashboard] = useState(null);  
const [statsLoading, setStatsLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardStats = async () => {
      try {
        const dashboard = await getDashboard();
setDashboard(dashboard);
setStats({

    domains:
        dashboard.innovation.breakdown.domains,

    keywords:
        dashboard.innovation.breakdown.keywords,

    technologyAreas:
        dashboard.innovation.breakdown.technology_areas,

    publications:
        dashboard.statistics.publications,

    patents:
        dashboard.statistics.patents,

    funding:
        dashboard.statistics.funding_opportunities,

    innovation:
        dashboard.innovation.innovation_score

});
        
      } catch (error) {
        console.error(
          "Failed to load dashboard statistics:",
          error
        );
      } finally {
        setStatsLoading(false);
      }
    };

    fetchDashboardStats();
  }, []);

  const modules = [
    {
      title: "Research Profile",
      description:
        "Manage your complete research profile, organization, domains, keywords and technology expertise",
      path: "/profile",
      icon: "RP",
    },
    
    {
      title: "Publications",
      description:
        "Add and manage journal articles, papers and research outputs.",
      path: "/profile/publications",
      icon: "PB",
      count: stats.publications,
    },
    {
      title: "Patents",
      description:
        "Maintain patent applications and innovation records.",
      path: "/profile/patents",
      icon: "PT",
      count: stats.patents,
    },

    {
  title: "Funding Opportunities",
  description: "Browse government and international funding programs.",
  path: "/funding",
  icon: "💰",
  count: stats.funding,
},
{
  title: "Grant Prediction",
  description: "Predict funding success using AI models.",
  path: "/grant-prediction",
  icon: "🎯",
},
{
  title: "Patent Landscape",
  description: "Analyze global patent trends and competitors.",
  path: "/patent-landscape",
  icon: "🌍",
},

{
  title: "Innovation Score",
  description:
    "View your AI-generated innovation score and detailed breakdown.",
  path: "/innovation-score",
  icon: "⭐",
  count: stats.innovation,
},

{
  title: "Research Trends",
  description: "Explore publication trends across research domains.",
  path: "/research-trends",
  icon: "📈",
},
  ];

  const totalStructuredRecords =
    stats.domains +
    stats.keywords +
    stats.technologyAreas +
    stats.publications +
    stats.patents;

  return (
    <div>
      <div className="dashboard-welcome">
        <div>
          <span className="dashboard-eyebrow">
            RESEARCHER WORKSPACE
          </span>

          <h1>
            Welcome back,{" "}
            {user?.full_name?.split(" ")[0] ||
              "Researcher"}
          </h1>

          <p>
            Manage your research identity, innovation
            records, and profile intelligence from one
            workspace.
          </p>
        </div>

        <div className="dashboard-account">
          <div className="dashboard-avatar">
            {user?.full_name
              ?.charAt(0)
              ?.toUpperCase() || "R"}
          </div>

          <div>
            <strong>
              {user?.full_name || "Researcher"}
            </strong>

            <span>{user?.email}</span>
          </div>
        </div>
      </div>

<div className="dashboard-stats">

  <div className="stat-card">
    <span className="stat-label">
      Research Domains
    </span>

    <strong>
      {statsLoading ? "..." : stats.domains}
    </strong>

    <small>Broad research fields</small>
  </div>

  <div className="stat-card">
    <span className="stat-label">
      Publications
    </span>

    <strong>
      {statsLoading ? "..." : stats.publications}
    </strong>

    <small>Scholarly research outputs</small>
  </div>

  <div className="stat-card">
    <span className="stat-label">
      Patents
    </span>

    <strong>
      {statsLoading ? "..." : stats.patents}
    </strong>

    <small>Intellectual property records</small>
  </div>

  <div className="stat-card">
    <span className="stat-label">
      Innovation Score
    </span>

    <strong>
      {statsLoading ? "..." : `${stats.innovation}/100`}
    </strong>

    <small>AI Calculated</small>
  </div>

  <div className="stat-card">
    <span className="stat-label">
      Profile Completion
    </span>

    <strong>
      {statsLoading
        ? "..."
        : `${dashboard?.profile_completion || 0}%`}
    </strong>

    <small>Research Profile</small>
  </div>

  <div className="stat-card">
    <span className="stat-label">
      Structured Records
    </span>

    <strong>
      {statsLoading
        ? "..."
        : totalStructuredRecords}
    </strong>

    <small className="positive-status">
      ● Live profile data
    </small>
  </div>

</div>

      <div className="dashboard-section-header">
        <div>
<h2>Research Intelligence Dashboard</h2>
          <p>
           Manage publications, patents, funding opportunities and AI-powered research intelligence from a unified platform.
          </p>
        </div>
      </div>

      <div className="module-grid">
        {modules.map((module) => (
          <Link
            key={module.path}
            to={module.path}
            className="module-card"
          >
            <div className="module-icon">
              {module.icon}
            </div>

            <div className="module-card-content">
              <div className="module-title-row">
                <h3>{module.title}</h3>

                {module.count !== undefined && (
                  <span className="module-record-count">
                    {statsLoading
                      ? "..."
                      : module.count}
                  </span>
                )}
              </div>

              <p>{module.description}</p>

              <span className="module-link-text">
                Open module →
              </span>
            </div>
          </Link>
        ))}
      </div>

      <div className="dashboard-section-header">
  <div>
    <h2>Latest Publications</h2>
    <p>Recently imported research publications.</p>
  </div>
</div>

<div className="module-grid">
  {dashboard?.latest_publications?.slice(0, 3).map((publication, index) => (
    <div key={index} className="module-card">
      <div className="module-card-content">
        <h3>{publication.title}</h3>

        <p>{publication.publisher}</p>

        <small>{publication.doi}</small>
      </div>
    </div>
  ))}
</div>

<div className="dashboard-section-header">
  <div>
    <h2>Latest Patents</h2>
    <p>Your most recent patent records.</p>
  </div>
</div>

<div className="module-grid">
  {dashboard?.latest_patents?.map((patent, index) => (
    <div key={index} className="module-card">
      <div className="module-card-content">
        <h3>{patent.title}</h3>

        <p>{patent.patent_office}</p>

        <span>{patent.status}</span>
      </div>
    </div>
  ))}
</div>

      
    </div>
  );
}

export default Dashboard;