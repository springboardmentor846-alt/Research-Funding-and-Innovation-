import { useEffect, useState } from "react";
import axios from "axios";
import PublicationTrend from "./PublicationTrend";
import EmergingTopics from "./EmergingTopics";
import ResearchHotspots from "./ResearchHotspots";
import PatentTrend from "./PatentTrend";
import CompetitorAnalysis from "./CompetitorAnalysis";
import TechnologyClusters from "./TechnologyClusters";
import TechnologyIntelligence from "./TechnologyIntelligence";
import InnovationScore from "./InnovationScore";
import CommercializationRecommendations from "./CommercializationRecommendations";
import ResearchProfileForm from "./ResearchProfileForm";
import LiveGrantsSearch from "./LiveGrantsSearch";
import "./Dashboard.css";

function Dashboard({ token, onLogout }) {
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState("");
  const [funding, setFunding] = useState([]);
  const [fundingError, setFundingError] = useState("");
  const [activeTab, setActiveTab] = useState("overview");
  const [allFunding, setAllFunding] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [profileDomains, setProfileDomains] = useState("");
  const [openGroups, setOpenGroups] = useState(["workspace", "research-group", "patents-group", "insights-group"]);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:8000/api/auth/me", {
          headers: { Authorization: `Bearer ${token}` },
        });
        setProfile(response.data);
      } catch (err) {
        setError("Could not load profile");
      }
    };

    fetchProfile();
  }, [token]);

  const fetchFunding = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:8000/api/funding/recommended", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setFunding(response.data);
      setFundingError("");
    } catch (err) {
      if (err.response && err.response.status === 404) {
        setFundingError("Create your research profile to see recommendations.");
      } else {
        setFundingError("Could not load funding recommendations.");
      }
    }
  };

  useEffect(() => {
    fetchFunding();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  useEffect(() => {
    const fetchAllFunding = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:8000/api/funding/");
        setAllFunding(response.data);
      } catch (err) {
        setAllFunding([]);
      }
    };
    fetchAllFunding();
  }, [token]);

  useEffect(() => {
    const fetchProfileDomains = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:8000/api/profile/", {
          headers: { Authorization: `Bearer ${token}` },
        });
        setProfileDomains(response.data.research_domains || "");
      } catch (err) {
        setProfileDomains("");
      }
    };
    fetchProfileDomains();
  }, [token, funding]);

  const getMatchInfo = (fundingItem) => {
    if (!profileDomains || !fundingItem.domains) return null;
    const userKw = profileDomains
      .split(",")
      .map((k) => k.trim().toLowerCase())
      .filter(Boolean);
    const fundKw = fundingItem.domains
      .split(",")
      .map((k) => k.trim().toLowerCase())
      .filter(Boolean);
    if (userKw.length === 0 || fundKw.length === 0) return null;

    const overlap = fundKw.filter((k) => userKw.includes(k)).length;
    const percent = Math.round((overlap / fundKw.length) * 100);

    let label = "Low Match";
    let color = "#9CA3AF";
    if (percent >= 70) {
      label = "Strong Match";
      color = "#1C8C7A";
    } else if (percent >= 35) {
      label = "Moderate Match";
      color = "#C9862B";
    }
    return { percent, label, color };
  };

  const filteredFunding = allFunding.filter((item) => {
    if (!searchTerm.trim()) return true;
    const term = searchTerm.toLowerCase();
    return (
      (item.title && item.title.toLowerCase().includes(term)) ||
      (item.domains && item.domains.toLowerCase().includes(term)) ||
      (item.source && item.source.toLowerCase().includes(term)) ||
      (item.description && item.description.toLowerCase().includes(term))
    );
  });

  const formatRole = (role) => {
    if (!role) return "";
    return role.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
  };

  const tabGroups = [
    {
      id: "workspace",
      label: "Workspace",
      items: [
        {
          id: "overview",
          label: "Overview",
          color: "#2E5EAA",
          icon: (
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="3" width="7" height="9" rx="1.5" />
              <rect x="14" y="3" width="7" height="5" rx="1.5" />
              <rect x="14" y="12" width="7" height="9" rx="1.5" />
              <rect x="3" y="16" width="7" height="5" rx="1.5" />
            </svg>
          ),
        },
      ],
    },
    {
      id: "research-group",
      label: "Research",
      items: [
        {
          id: "research-profile",
          label: "Profile",
          color: "#1C8C7A",
          icon: (
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="8" r="4" />
              <path d="M4 21c0-4 3.6-7 8-7s8 3 8 7" />
            </svg>
          ),
        },
        {
          id: "research-trends",
          label: "Trends",
          color: "#1C8C7A",
          icon: (
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 17l6-6 4 4 8-8" />
              <path d="M15 7h6v6" />
            </svg>
          ),
        },
      ],
    },
    {
      id: "patents-group",
      label: "Patents",
      items: [
        {
          id: "patents",
          label: "Landscape",
          color: "#C9862B",
          icon: (
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <path d="M14 2v6h6" />
            </svg>
          ),
        },
      ],
    },
    {
      id: "insights-group",
      label: "Insights",
      items: [
        {
          id: "tech-intelligence",
          label: "Technology",
          color: "#B0479B",
          icon: (
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 18h6" />
              <path d="M10 22h4" />
              <path d="M12 2a7 7 0 0 0-4 12.7c.6.5 1 1.3 1 2.1V17h6v-2.2c0-.8.4-1.6 1-2.1A7 7 0 0 0 12 2z" />
            </svg>
          ),
        },
        {
          id: "commercialization",
          label: "Commercialization",
          color: "#B0479B",
          icon: (
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 3v18h18" />
              <path d="M18 9l-5 5-4-4-4 4" />
            </svg>
          ),
        },
        {
          id: "funding",
          label: "Funding",
          color: "#2E5EAA",
          icon: (
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="9" />
              <path d="M12 7v10M9.5 9.5c0-1.4 1.1-2.2 2.5-2.2s2.5.8 2.5 2c0 1.5-1.3 1.9-2.5 2.3-1.3.4-2.5.9-2.5 2.4 0 1.2 1.1 2 2.5 2s2.5-.8 2.5-2.2" />
            </svg>
          ),
        },
      ],
    },
  ];

  const handleGroupClick = (groupId) => {
    setOpenGroups((prev) =>
      prev.includes(groupId) ? prev.filter((g) => g !== groupId) : [...prev, groupId]
    );
  };

  const handleItemClick = (groupId, itemId) => {
    setActiveTab(itemId);
  };

  return (
    <div className="dash-page">
      <div className="dash-navbar">
        <div className="dash-brand">
          Research Funding &amp; <span className="highlight">Innovation Intelligence</span>
        </div>
        <div className="dash-nav-right">
          {profile && (
            <span className="dash-role-badge">{formatRole(profile.role)}</span>
          )}
          <button className="dash-logout" onClick={onLogout}>
            Logout
          </button>
        </div>
      </div>

      <div className="dash-body">
        <div className="dash-sidebar">
          <div className="sidebar-groups-wrap">
            {tabGroups.map((group) => {
              const isOpen = openGroups.includes(group.id);
              const hasActiveChild = group.items.some((item) => item.id === activeTab);
              return (
                <div className="sidebar-group" key={group.id}>
                  <button
                    className={`sidebar-group-header ${isOpen ? "open" : ""} ${hasActiveChild ? "has-active" : ""}`}
                    onClick={() => handleGroupClick(group.id)}
                  >
                    <span>{group.label}</span>
                    <span className={`sidebar-chevron ${isOpen ? "rotated" : ""}`}>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                        <path d="M9 18l6-6-6-6" />
                      </svg>
                    </span>
                  </button>

                  <div className={`sidebar-group-items ${isOpen ? "expanded" : "collapsed"}`}>
                    {group.items.map((item) => (
                      <button
                        key={item.id}
                        className={`sidebar-item ${activeTab === item.id ? "active" : ""}`}
                        onClick={() => handleItemClick(group.id, item.id)}
                      >
                        <span className="sidebar-icon" style={{ color: item.color }}>
                          {item.icon}
                        </span>
                        {item.label}
                      </button>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>

          {profile && (
            <div className="sidebar-footer">
              <div className="sidebar-footer-avatar">
                {profile.email.charAt(0).toUpperCase()}
              </div>
              <div>
                <div className="sidebar-footer-name">{profile.email.split("@")[0]}</div>
                <div className="sidebar-footer-role">{formatRole(profile.role)}</div>
              </div>
            </div>
          )}
        </div>

        <div className="dash-main">
          <div className="dash-welcome">
            <h1>Welcome back{profile ? `, ${profile.email.split("@")[0]}` : ""}</h1>
            <p>Here's what's happening across your funding, research and patent landscape.</p>
          </div>

          {error && <p className="dash-error">{error}</p>}

          {activeTab === "overview" && (
            <>
              {profile && (
                <div className="dash-card">
                  <h3>Your Profile</h3>
                  <p className="dash-card-subtitle">Account details</p>
                  <p><strong>Email:</strong> {profile.email}</p>
                  <p><strong>Role:</strong> {formatRole(profile.role)}</p>
                </div>
              )}

              <div className="dash-card">
                <h3>Innovation Score</h3>
                <p className="dash-card-subtitle">Your overall innovation potential, based on research, patents, technology and funding fit</p>
                <InnovationScore token={token} />
              </div>
            </>
          )}

          {activeTab === "research-profile" && (
            <ResearchProfileForm token={token} onProfileSaved={fetchFunding} />
          )}

          {activeTab === "research-trends" && (
            <>
              <div className="dash-card">
                <h3>Publication Trend</h3>
                <p className="dash-card-subtitle">Your research output over time</p>
                <PublicationTrend />
              </div>

              <div className="dash-card">
                <h3>Emerging Topics</h3>
                <p className="dash-card-subtitle">Trending keywords from recent research</p>
                <EmergingTopics />
              </div>

              <div className="dash-card">
                <h3>Research Hotspots</h3>
                <p className="dash-card-subtitle">Most active research areas overall</p>
                <ResearchHotspots />
              </div>
            </>
          )}

          {activeTab === "patents" && (
            <>
              <div className="dash-card">
                <h3>Patent Trend</h3>
                <p className="dash-card-subtitle">Patent filings over time</p>
                <PatentTrend />
              </div>

              <div className="dash-card">
                <h3>Competitor Analysis</h3>
                <p className="dash-card-subtitle">Most active patent holders</p>
                <CompetitorAnalysis />
              </div>

              <div className="dash-card">
                <h3>Technology Clusters</h3>
                <p className="dash-card-subtitle">Innovation mapping from patent titles</p>
                <TechnologyClusters />
              </div>
            </>
          )}

          {activeTab === "tech-intelligence" && (
            <div className="dash-card">
              <h3>Technology Intelligence</h3>
              <p className="dash-card-subtitle">Cross-domain technology maturity — research + patents combined</p>
              <TechnologyIntelligence />
            </div>
          )}

          {activeTab === "commercialization" && (
            <div className="dash-card">
              <h3>Commercialization Recommendations</h3>
              <p className="dash-card-subtitle">Actionable next steps based on your innovation profile</p>
              <CommercializationRecommendations token={token} />
            </div>
          )}

          {activeTab === "funding" && (
            <>
              <div className="dash-card">
                <h3>Search Real US Federal Grants</h3>
                <p className="dash-card-subtitle">Live search from Grants.gov — the official U.S. government grants database</p>
                <LiveGrantsSearch token={token} />
              </div>

              <div className="dash-card">
                <h3>Search Funding Opportunities</h3>
                <p className="dash-card-subtitle">
                  Search all available funding opportunities by keyword (e.g. AI, Blockchain, Security)
                </p>
                <input
                  type="text"
                  placeholder="Search by keyword... e.g. AI"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  style={{
                    width: "100%",
                    padding: "10px 12px",
                    marginTop: "6px",
                    marginBottom: "14px",
                    border: "1px solid #d7dce3",
                    borderRadius: "6px",
                    fontSize: "14px",
                    boxSizing: "border-box",
                  }}
                />

                {searchTerm.trim() && filteredFunding.length === 0 && (
                  <p className="dash-empty">No funding opportunities match "{searchTerm}".</p>
                )}

                {searchTerm.trim() && filteredFunding.length > 0 && (
                  <div className="funding-grid">
                    {filteredFunding.map((item) => {
                      const match = getMatchInfo(item);
                      return (
                        <div key={item.id} className="funding-item">
                          {match && (
                            <span
                              style={{
                                display: "inline-block",
                                background: match.color,
                                color: "#fff",
                                fontSize: "11px",
                                fontWeight: 700,
                                padding: "3px 9px",
                                borderRadius: "12px",
                                marginBottom: "6px",
                              }}
                            >
                              {match.label} · {match.percent}%
                            </span>
                          )}
                          <h4>{item.title}</h4>
                          <div className="funding-meta">
                            <span className="funding-tag">{item.source}</span>
                            <span className="funding-amount">{item.amount}</span>
                          </div>
                          <p style={{ fontSize: "13px", color: "var(--slate)" }}>
                            <strong>Deadline:</strong> {item.deadline}
                          </p>
                          <p className="funding-desc">{item.description}</p>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

              <div className="dash-card">
                <h3>Recommended Funding</h3>
                <p className="dash-card-subtitle">Opportunities matched to your research profile</p>

                {fundingError && <p className="dash-empty">{fundingError}</p>}

                {!fundingError && funding.length === 0 && (
                  <p className="dash-empty">No matching funding opportunities right now.</p>
                )}

                {funding.length > 0 && (
                  <div className="funding-grid">
                    {funding.map((item) => {
                      const match = getMatchInfo(item);
                      return (
                        <div key={item.id} className="funding-item">
                          {match && (
                            <span
                              style={{
                                display: "inline-block",
                                background: match.color,
                                color: "#fff",
                                fontSize: "11px",
                                fontWeight: 700,
                                padding: "3px 9px",
                                borderRadius: "12px",
                                marginBottom: "6px",
                              }}
                            >
                              {match.label} · {match.percent}%
                            </span>
                          )}
                          <h4>{item.title}</h4>
                          <div className="funding-meta">
                            <span className="funding-tag">{item.source}</span>
                            <span className="funding-amount">{item.amount}</span>
                          </div>
                          <p style={{ fontSize: "13px", color: "var(--slate)" }}>
                            <strong>Deadline:</strong> {item.deadline}
                          </p>
                          <p className="funding-desc">{item.description}</p>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;