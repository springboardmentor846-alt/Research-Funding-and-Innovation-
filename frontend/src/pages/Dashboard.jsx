import { useEffect, useState } from "react";
import { Link, useOutletContext } from "react-router-dom";
import api from "../api/axios";

function Dashboard() {
  const { user } = useOutletContext();

  const [stats, setStats] = useState({
    domains: 0,
    keywords: 0,
    technologyAreas: 0,
    publications: 0,
    patents: 0,
  });

  const [statsLoading, setStatsLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardStats = async () => {
      try {
        const [
          domainsResponse,
          keywordsResponse,
          technologyResponse,
          publicationsResponse,
          patentsResponse,
        ] = await Promise.all([
          api.get("/research-profiles/me/domains"),
          api.get("/research-profiles/me/keywords"),
          api.get("/research-profiles/me/technology-areas"),
          api.get("/research-profiles/me/publications"),
          api.get("/research-profiles/me/patents"),
        ]);

        setStats({
          domains:
            domainsResponse.data.domains?.length || 0,

          keywords:
            keywordsResponse.data.keywords?.length || 0,

          technologyAreas:
            technologyResponse.data.technology_areas
              ?.length || 0,

          publications:
            publicationsResponse.data.publications
              ?.length || 0,

          patents:
            patentsResponse.data.patents?.length || 0,
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
        "Manage academic background, position, organization and ORCID.",
      path: "/profile",
      icon: "RP",
    },
    {
      title: "Research Domains",
      description:
        "Define your primary fields and areas of research.",
      path: "/profile/domains",
      icon: "RD",
      count: stats.domains,
    },
    {
      title: "Keywords",
      description:
        "Add focused research topics used for intelligent matching.",
      path: "/profile/keywords",
      icon: "KW",
      count: stats.keywords,
    },
    {
      title: "Technology Areas",
      description:
        "Maintain technologies, platforms and technical expertise.",
      path: "/profile/technology-areas",
      icon: "TA",
      count: stats.technologyAreas,
    },
    {
      title: "Organization",
      description:
        "Manage institutional and departmental information.",
      path: "/profile/organization",
      icon: "OR",
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

          <small>
            Broad research fields
          </small>
        </div>

        <div className="stat-card">
          <span className="stat-label">
            Publications
          </span>

          <strong>
            {statsLoading ? "..." : stats.publications}
          </strong>

          <small>
            Scholarly research outputs
          </small>
        </div>

        <div className="stat-card">
          <span className="stat-label">
            Patents
          </span>

          <strong>
            {statsLoading ? "..." : stats.patents}
          </strong>

          <small>
            Intellectual property records
          </small>
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
          <h2>Research Profile Management</h2>

          <p>
            Build a structured research identity for future
            funding and innovation intelligence workflows.
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
    </div>
  );
}

export default Dashboard;