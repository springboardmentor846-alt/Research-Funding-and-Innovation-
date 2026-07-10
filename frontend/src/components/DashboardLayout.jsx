import { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";

function DashboardLayout({ children, user }) {
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState(false);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    navigate("/login");
  };

  const navItems = [
    { path: "/dashboard", label: "Home", icon: "▦" },
    { path: "/profile", label: "Research Profile", icon: "◉" },
    { path: "/profile/domains", label: "Research Domains", icon: "◇" },
    { path: "/profile/keywords", label: "Keywords", icon: "#" },
    { path: "/profile/technology-areas", label: "Technology Areas", icon: "⌘" },
    { path: "/profile/organization", label: "Organization", icon: "▣" },
    { path: "/profile/publications", label: "Publications", icon: "▤" },
    { path: "/profile/patents", label: "Patents", icon: "◆" },
  ];

  return (
    <div className={`app-shell ${collapsed ? "sidebar-collapsed" : ""}`}>
      <aside className="app-sidebar">
        <div className="sidebar-brand">
          <div className="brand-mark">IF</div>

          {!collapsed && (
            <div className="brand-text">
              <h5>InnovFund</h5>
              <span>Research Intelligence</span>
            </div>
          )}
        </div>

        {!collapsed && (
          <div className="sidebar-section-label">
            WORKSPACE
          </div>
        )}

        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === "/dashboard"}
              title={collapsed ? item.label : ""}
              className={({ isActive }) =>
                `sidebar-link ${isActive ? "active" : ""}`
              }
            >
              <span className="sidebar-icon">
                {item.icon}
              </span>

              {!collapsed && <span>{item.label}</span>}
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-user">
          <div className="user-avatar">
            {user?.full_name?.charAt(0)?.toUpperCase() || "R"}
          </div>

          {!collapsed && (
            <div className="sidebar-user-info">
              <strong>{user?.full_name || "Researcher"}</strong>
              <span>{user?.role || "researcher"}</span>
            </div>
          )}

          {!collapsed && (
            <button
              className="logout-icon-btn"
              onClick={handleLogout}
              title="Logout"
            >
              ↪
            </button>
          )}
        </div>
      </aside>

      <main className="app-main">
        <header className="app-topbar">
          <div className="d-flex align-items-center gap-3">
            <button
              className="sidebar-toggle-btn"
              onClick={() => setCollapsed(!collapsed)}
              aria-label="Toggle sidebar"
              title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
            >
              ☰
            </button>

            <span className="topbar-label">
              RESEARCH FUNDING & INNOVATION PLATFORM
            </span>
          </div>

          <div className="topbar-status">
            <span className="status-dot"></span>
            System Online
          </div>
        </header>

        <div className="app-content">
          {children}
        </div>
      </main>
    </div>
  );
}

export default DashboardLayout;