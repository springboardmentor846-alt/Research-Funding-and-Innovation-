import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
  ArrowRight,
  Building2,
  CalendarDays,
  Code2,
  Handshake,
  MapPin,
  Rocket,
  Sparkles,
  Wallet,
  Users,
} from "lucide-react";
import { getStartupProfile } from "../../api/startup";
import { getCollaborationRequests } from "../../api/collaboration";

const modules = [
  { to: "/startup/profile", title: "Startup Profile", text: "Manage your startup information", icon: Rocket, tone: "blue" },
  { to: "/startup/researchers", title: "Find Researchers", text: "Discover expert researchers", icon: Users, tone: "green" },
  { to: "/startup/startups", title: "Find Startups", text: "Connect with other startups", icon: Building2, tone: "orange" },
  { to: "/startup/funding", title: "Funding Opportunities", text: "Explore funding and grants", icon: Wallet, tone: "green" },
  { to: "/startup/predict-success", title: "Predict Success", text: "Analyze funding potential", icon: Sparkles, tone: "purple" },
];

function completion(profile) {
  if (!profile) return 0;
  const fields = [
    "startup_name", "tagline", "industry", "stage", "founded_year", "funding_stage",
    "startup_email", "website", "location", "description", "technology_stack",
    "research_interests", "funding_needed", "team_size", "problem_statement", "solution",
  ];
  const filled = fields.filter((field) => profile[field] !== null && profile[field] !== undefined && String(profile[field]).trim() !== "").length;
  return Math.round((filled / fields.length) * 100);
}

export default function StartupDashboard() {
  const [profile, setProfile] = useState(null);
  const [requests, setRequests] = useState({ incoming: [], outgoing: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.allSettled([getStartupProfile(), getCollaborationRequests()]).then(([profileResult, requestResult]) => {
      if (profileResult.status === "fulfilled") setProfile(profileResult.value);
      if (requestResult.status === "fulfilled") setRequests(requestResult.value);
      setLoading(false);
    });
  }, []);

  const profileCompletion = useMemo(() => completion(profile), [profile]);
  const pendingRequests = [...(requests.incoming || []), ...(requests.outgoing || [])].filter((item) => item.status === "pending").length;

  if (loading) {
    return <div className="startup-loading">Loading startup workspace...</div>;
  }

  const startupName = profile?.startup_name || "Your Startup";

  return (
    <div className="startup-page">
      <div className="startup-page-header">
        <span className="startup-eyebrow">STARTUP WORKSPACE</span>
        <h1>Startup Founder Dashboard</h1>
        <p>Manage your startup profile, discover researchers, find other startups and explore funding opportunities from one workspace.</p>
      </div>

      <section className="startup-panel startup-overview-panel">
        <div className="startup-panel-heading">
          <div>
            <span className="startup-eyebrow">STARTUP OVERVIEW</span>
            <h2>{startupName}</h2>
            <p>{profile?.tagline || "Your startup intelligence and funding workspace."}</p>
          </div>
        </div>

        <div className="startup-overview-grid">
          <div className="startup-overview-item">
            <Rocket />
            <div><span>Startup Stage</span><strong>{profile?.stage || "Not set"}</strong></div>
          </div>
          <div className="startup-overview-item">
            <Wallet />
            <div><span>Funding Stage</span><strong>{profile?.funding_stage || "Not set"}</strong></div>
          </div>
          <div className="startup-overview-item">
            <Users />
            <div><span>Team Size</span><strong>{profile?.team_size || 0}</strong></div>
          </div>
          <div className="startup-overview-item">
            <Handshake />
            <div><span>Pending Requests</span><strong>{pendingRequests}</strong></div>
          </div>
        </div>
      </section>

      <section className="startup-panel startup-profile-progress">
        <div className="startup-panel-heading startup-progress-heading">
          <div>
            <span className="startup-eyebrow">STARTUP PROFILE</span>
            <h2>{profileCompletion}% Complete</h2>
            <p>{profileCompletion >= 80 ? "Your startup profile is looking good." : "Complete your profile to improve matching and funding recommendations."}</p>
          </div>
          <Link className="startup-primary-button" to="/startup/profile">
            Complete Profile <ArrowRight size={17} />
          </Link>
        </div>
        <div className="startup-progress-track"><span style={{ width: `${profileCompletion}%` }} /></div>
      </section>

      <section className="startup-panel">
        <div className="startup-panel-heading">
          <span className="startup-eyebrow">STARTUP INFORMATION</span>
          <h2>Your Startup</h2>
          <p>Key information from your startup profile.</p>
        </div>
        <div className="startup-info-grid">
          <Info icon={Building2} label="Industry" value={profile?.industry || "Not specified"} />
          <Info icon={Code2} label="Technology Stack" value={profile?.technology_stack || "Not specified"} />
          <Info icon={Wallet} label="Funding Needed" value={profile?.funding_needed || "Not specified"} />
          <Info icon={MapPin} label="Location" value={profile?.location || "Not specified"} />
          <Info icon={CalendarDays} label="Founded Year" value={profile?.founded_year || "Not specified"} />
        </div>
      </section>

      <section className="startup-panel startup-quick-access">
        <div className="startup-panel-heading">
          <span className="startup-eyebrow">QUICK ACCESS</span>
          <h2>Explore Startup Modules</h2>
          <p>Access the tools and insights available for your startup.</p>
        </div>
        <div className="startup-modules-grid">
          {modules.map(({ to, title, text, icon: Icon, tone }) => (
            <Link key={to} to={to} className="startup-module-card">
              <span className={`startup-module-icon ${tone}`}><Icon size={22} /></span>
              <span className="startup-module-copy"><strong>{title}</strong><small>{text}</small></span>
              <ArrowRight className="startup-module-arrow" size={20} />
            </Link>
          ))}
        </div>
      </section>

      <section className="startup-panel startup-recent-panel">
        <div className="startup-panel-heading startup-recent-heading">
          <div>
            <span className="startup-eyebrow">RECENT ACTIVITY</span>
            <h2>Recent Activity</h2>
            <p>Your startup activity will appear here.</p>
          </div>
          <Link to="/startup/requests" className="startup-text-link">View requests <ArrowRight size={16} /></Link>
        </div>
        <div className="startup-empty-state">
          <Sparkles size={34} />
          <strong>No recent activity</strong>
          <span>Start exploring researchers, startups and funding opportunities to see activity here.</span>
        </div>
      </section>
    </div>
  );
}

function Info({ icon: Icon, label, value }) {
  return (
    <div className="startup-info-item">
      <Icon size={22} />

      <div className="startup-info-item-content">
        <span>{label}</span>
        <strong>{value}</strong>
      </div>
    </div>
  );
}
