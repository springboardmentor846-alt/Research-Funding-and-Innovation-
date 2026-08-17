import { useState } from "react";
import { NavLink, Outlet, useNavigate, useOutletContext } from "react-router-dom";
import {
  BarChart3,
  Building2,
  Handshake,
  Lightbulb,
  Search,
  Wallet,
  LogOut,
  Menu,
} from "lucide-react";
import "../../styles/startup.css";

const navGroups = [
  {
    heading: "Workspace",
    items: [
      { path: "/startup/dashboard", label: "Dashboard", icon: BarChart3 },
    ],
  },
  {
    heading: "Startup",
    items: [
      { path: "/startup/profile", label: "Startup Profile", icon: Building2 },
    ],
  },
  {
    heading: "Collaboration",
    items: [
      { path: "/startup/researchers", label: "Find Researchers", icon: Search },
      { path: "/startup/startups", label: "Find Startups", icon: Handshake },
      { path: "/startup/requests", label: "Collaboration Requests", icon: Handshake },
    ],
  },
  {
    heading: "Funding",
    items: [
      { path: "/startup/funding", label: "Funding Opportunities", icon: Wallet },
    ],
  },
];

export default function StartupLayout() {
  const { user } = useOutletContext();
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState(false);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("role");
    localStorage.removeItem("full_name");
    navigate("/login", { replace: true });
  };

  return (
    <div className={`startup-shell ${collapsed ? "startup-sidebar-collapsed" : ""}`}>
      <aside className="startup-sidebar">
        <div className="startup-brand">
          <div className="startup-brand-mark">IF</div>
          {!collapsed && (
            <div>
              <strong>InnovFund</strong>
              <span>Research Intelligence</span>
            </div>
          )}
        </div>

        <nav className="startup-nav">
          {navGroups.map((group) => (
            <div className="startup-nav-group" key={group.heading}>
              {!collapsed && <div className="startup-nav-heading">{group.heading}</div>}
              {group.items.map(({ path, label, icon: Icon }) => (
                <NavLink
                  key={path}
                  to={path}
                  end={path === "/startup/dashboard"}
                  className={({ isActive }) =>
                    `startup-nav-link ${isActive ? "active" : ""}`
                  }
                >
                  <Icon size={17} strokeWidth={1.9} />
                  {!collapsed && <span>{label}</span>}
                </NavLink>
              ))}
            </div>
          ))}
        </nav>

        <div className="startup-sidebar-user">
          <div className="startup-user-avatar">
            {(user?.full_name || localStorage.getItem("full_name") || "S").charAt(0).toUpperCase()}
          </div>
          {!collapsed && (
            <div className="startup-user-text">
              <strong>{user?.full_name || localStorage.getItem("full_name") || "Startup Founder"}</strong>
              <span>Startup Founder</span>
            </div>
          )}
          <button className="startup-logout" onClick={handleLogout} title="Logout">
            <LogOut size={17} />
          </button>
        </div>
      </aside>

      <main className="startup-main">
        <header className="startup-topbar">
          <button
            className="startup-menu-button"
            onClick={() => setCollapsed((value) => !value)}
            aria-label="Toggle sidebar"
          >
            <Menu size={20} />
          </button>
          <span className="startup-topbar-label">RESEARCH FUNDING &amp; INNOVATION PLATFORM</span>
          <span className="startup-online"><i /> System Online</span>
        </header>

        <div className="startup-content">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
