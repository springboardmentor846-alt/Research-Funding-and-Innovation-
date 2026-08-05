import { useState } from "react";
import {
  NavLink,
  useNavigate,
  Outlet,
  useOutletContext,
} from "react-router-dom";

function StartupLayout() {
  const { user } = useOutletContext();

  const navigate = useNavigate();

  const [collapsed, setCollapsed] = useState(false);

const handleLogout = () => {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("role");
  navigate("/login");
};

const navItems = [

  {
    heading: "Workspace",
    items: [
      {
        path: "/startup/dashboard",
        label: "Dashboard",
        icon: "📊",
      },
    ],
  },

  {
    heading: "Startup",
    items: [
      {
        path: "/startup/profile",
        label: "Startup Profile",
        icon: "🏢",
      },
    ],
  },

  {
    heading: "Collaboration",
    items: [
      {
        path: "/startup/researchers",
        label: "Find Researchers",
        icon: "👨‍🔬",
      },
      {
        path: "/startup/requests",
        label: "Collaboration Requests",
        icon: "🤝",
      },
    ],
  },

  {
    heading: "Funding",
    items: [
      {
        path: "/startup/funding",
        label: "Funding Opportunities",
        icon: "💰",
      },
    ],
  },

  {
    heading: "AI Insights",
    items: [
      {
        path: "/startup/innovation-score",
        label: "Innovation Score",
        icon: "⭐",
      },
    ],
  },

];

  return (
    <div className={`app-shell ${collapsed ? "sidebar-collapsed" : ""}`}>
      {/* Sidebar */}

      <aside className="app-sidebar">

        <div className="sidebar-brand">

          <div className="brand-mark">
            IF
          </div>

          {!collapsed && (
            <div className="brand-text">
              <h5>InnovFund</h5>

              <span>
                Research Intelligence
              </span>
            </div>
          )}

        </div>

        <nav className="sidebar-nav">

          {navItems.map((group) => (

            <div key={group.heading}>

              {!collapsed && (
                <div className="sidebar-section-label">
                  {group.heading.toUpperCase()}
                </div>
              )}

              {group.items.map((item) => (

                <NavLink
                  key={item.path}
                  to={item.path}
                  end={item.path === "/startup/dashboard"}
                  className={({ isActive }) =>
                    `sidebar-link ${isActive ? "active" : ""}`
                  }
                >

                  <span className="sidebar-icon">
                    {item.icon}
                  </span>

                  {!collapsed && (
                    <span>
                      {item.label}
                    </span>
                  )}

                </NavLink>

              ))}

            </div>

          ))}

        </nav>

        {/* Bottom user */}

        <div className="sidebar-user">

          <div className="user-avatar">

            {user?.full_name?.charAt(0)?.toUpperCase() || "S"}

          </div>

          {!collapsed && (

            <div className="sidebar-user-info">

              <strong>

                {user?.full_name || "Startup Founder"}

              </strong>

              <span>

                {user?.role || "startup_founder"}

              </span>

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

      {/* Main */}

      <main className="app-main">

        <header className="app-topbar">

          <div className="d-flex align-items-center gap-3">

            <button
              className="sidebar-toggle-btn"
              onClick={() =>
                setCollapsed(!collapsed)
              }
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

          <Outlet />

        </div>

      </main>

    </div>
  );
}

export default StartupLayout;