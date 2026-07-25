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
  const [pubCount, setPubCount] = useState(null);
  const [patentCount, setPatentCount] = useState(null);

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

  useEffect(() => {
    const fetchCounts = async () => {
      try {
        const pubRes = await axios.get("http://127.0.0.1:8000/api/profile/publications", {
          headers: { Authorization: `Bearer ${token}` },
        });
        setPubCount(pubRes.data.length);
      } catch (err) {
        setPubCount(0);
      }
      try {
        const patRes = await axios.get("http://127.0.0.1:8000/api/profile/patents", {
          headers: { Authorization: `Bearer ${token}` },
        });
        setPatentCount(patRes.data.length);
      } catch (err) {
        setPatentCount(0);
      }
    };
    fetchCounts();
  }, [token]);

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

  const tabs = [
    {
      id: "overview",
      label: "Overview",
      icon: (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <rect x="3" y="3" width="7" height="9" rx="1.5" />
          <rect x="14" y="3" width="7" height="5" rx="1.5" />
          <rect x="14" y="12" width="7" height="9" rx="1.5" />
          <rect x="3" y="16" width="7" height="5" rx="1.5" />
        </svg>
      ),
    },
    {
      id: "research",
      label: "Research",
      icon: (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
          <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
        </svg>
      ),
    },
    {
      id: "patents",
      label: "Patents",
      icon: (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
          <path d="M14 2v6h6" />
        </svg>
      ),
    },
    {
      id: "innovation",
      label: "Innovation",
      icon: (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M9 18h6" />
          <path d="M10 22h4" />
          <path d="M12 2a7 7 0 0 0-4 12.7c.6.5 1 1.3 1 2.1V17h6v-2.2c0-.8.4-1.6 1-2.1A7 7 0 0 0 12 2z" />
        </svg>
      ),
    },
    {
      id: "funding",
      label: "Funding",
      icon: (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="9" />
          <path d="M12 7v10M9.5 9.5c0-1.4 1.1-2.2 2.5-2.2s2.5.8 2.5 2c0 1.5-1.3 1.9-2.5 2.3-1.3.4-2.5.9-2.5 2.4 0 1.2 1.1 2 2.5 2s2.5-.8 2.5-2.2" />
        </svg>
      ),
    },
  ];

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
          {tabs.map((tab) => (
            <button
              key={tab.id}
              className={`sidebar-item ${activeTab === tab.id ? "active" : ""}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <span className="sidebar-icon">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>

        <div className="dash-main">
          <div className="dash-welcome">
            <h1>Welcome back{profile ? `, ${profile.email.split("@")[0]}` : ""}</h1>
            <p>Here's what's happening across your funding, research and patent landscape.</p>
          </div>

          {error && <p className="dash-error">{error}</p>}

          {activeTab === "overview" && (
            <>
              <div className="stats-strip">
                <div className="stat-box">
                  <span className="stat-number">{pubCount === null ? "—" : pubCount}</span>
                  <span className="stat-label">Publications</span>
                </div>
                <div className="stat-box">
                  <span className="stat-number">{patentCount === null ? "—" : patentCount}</span>
                  <span className="stat-label">Patents</span>
                </div>
                <div className="stat-box">
                  <span className="stat-number">{funding.length}</span>
                  <span className="stat-label">Funding Matches</span>
                </div>
              </div>

              {profile && (
                <div className="dash-card">
                  <div className="profile-header-row">
                    <div className="profile-avatar">
                      {profile.email.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <h3 style={{ marginBottom: "2px" }}>Your Profile</h3>
                      <p className="dash-card-subtitle" style={{ marginBottom: 0 }}>Account details</p>
                    </div>
                  </div>
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

          {activeTab === "research" && (
            <>
              <ResearchProfileForm token={token} onProfileSaved={fetchFunding} />

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

          {activeTab === "innovation" && (
            <>
              <div className="dash-card">
                <h3>Technology Intelligence</h3>
                <p className="dash-card-subtitle">Cross-domain technology maturity — research + patents combined</p>
                <TechnologyIntelligence />
              </div>

              <div className="dash-card">
                <h3>Commercialization Recommendations</h3>
                <p className="dash-card-subtitle">Actionable next steps based on your innovation profile</p>
                <CommercializationRecommendations token={token} />
              </div>
            </>
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