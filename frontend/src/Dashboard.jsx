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
import "./Dashboard.css";

function Dashboard({ token, onLogout }) {
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState("");
  const [funding, setFunding] = useState([]);
  const [fundingError, setFundingError] = useState("");

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

  useEffect(() => {
    const fetchFunding = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:8000/api/funding/recommended", {
          headers: { Authorization: `Bearer ${token}` },
        });
        setFunding(response.data);
      } catch (err) {
        if (err.response && err.response.status === 404) {
          setFundingError("Create your research profile to see recommendations.");
        } else {
          setFundingError("Could not load funding recommendations.");
        }
      }
    };

    fetchFunding();
  }, [token]);

  const formatRole = (role) => {
    if (!role) return "";
    return role.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
  };

  return (
    <div className="dash-page">
      {/* NAVBAR */}
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

      {/* CONTENT */}
      <div className="dash-content">
        <div className="dash-welcome">
          <h1>Welcome back{profile ? `, ${profile.email.split("@")[0]}` : ""}</h1>
          <p>Here's what's happening across your funding, research and patent landscape.</p>
        </div>

        {error && <p className="dash-error">{error}</p>}

        {profile && (
          <div className="dash-card">
            <h3>Your Profile</h3>
            <p className="dash-card-subtitle">Account details</p>
            <p><strong>Email:</strong> {profile.email}</p>
            <p><strong>Role:</strong> {formatRole(profile.role)}</p>
          </div>
        )}

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
        
        <div className="dash-card">
          <h3>Technology Intelligence</h3>
          <p className="dash-card-subtitle">Cross-domain technology maturity — research + patents combined</p>
          <TechnologyIntelligence />
        </div>
        <div className="dash-card">
          <h3>Innovation Score</h3>
          <p className="dash-card-subtitle">Your overall innovation potential, based on research, patents, technology and funding fit</p>
          <InnovationScore token={token} />
        </div>
        <div className="dash-card">
          <h3>Commercialization Recommendations</h3>
          <p className="dash-card-subtitle">Actionable next steps based on your innovation profile</p>
          <CommercializationRecommendations token={token} />
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
              {funding.map((item) => (
                <div key={item.id} className="funding-item">
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
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;