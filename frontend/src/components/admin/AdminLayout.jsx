import { useState } from "react";
import {
  NavLink,
  Outlet,
  useNavigate,
  useOutletContext,
} from "react-router-dom";
import {
  BarChart3,
  Users,
  ShieldCheck,
  LogOut,
  Menu,
} from "lucide-react";
import "../../styles/admin.css";

const navGroups = [
  {
    heading: "Overview",
    items: [
      { path: "/admin/dashboard", label: "Dashboard", icon: BarChart3 },
    ],
  },
  {
    heading: "Administration",
    items: [
      { path: "/admin/users", label: "User Management", icon: Users },
    ],
  },
];

export default function AdminLayout() {
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
    <div className={`admin-shell ${collapsed ? "admin-sidebar-collapsed" : ""}`}>
      <aside className="admin-sidebar">
        <div className="admin-brand">
          <div className="admin-brand-mark">IF</div>
          {!collapsed && (
            <div className="admin-brand-copy">
              <strong>InnovFund</strong>
              <span>Administration</span>
            </div>
          )}
        </div>

        {!collapsed && (
          <div className="admin-security-badge">
            <ShieldCheck size={14} />
            <span>Administrator Console</span>
          </div>
        )}

        <nav className="admin-nav" aria-label="Administrator navigation">
          {navGroups.map((group) => (
            <div className="admin-nav-group" key={group.heading}>
              {!collapsed && (
                <div className="admin-nav-heading">
                  {group.heading}
                </div>
              )}

              {group.items.map(({ path, label, icon: Icon }) => (
                <NavLink
                  key={path}
                  to={path}
                  className={({ isActive }) =>
                    `admin-nav-link ${isActive ? "active" : ""}`
                  }
                >
                  <Icon size={17} strokeWidth={1.9} />
                  {!collapsed && <span>{label}</span>}
                </NavLink>
              ))}
            </div>
          ))}
        </nav>

        <div className="admin-sidebar-user">
          <div className="admin-user-avatar">
            {(user?.full_name || localStorage.getItem("full_name") || "A")
              .charAt(0)
              .toUpperCase()}
          </div>

          {!collapsed && (
            <div className="admin-user-copy">
              <strong>
                {user?.full_name || localStorage.getItem("full_name") || "Administrator"}
              </strong>
              <span>Administrator</span>
            </div>
          )}

          <button
            className="admin-logout"
            onClick={handleLogout}
            title="Logout"
            aria-label="Logout"
          >
            <LogOut size={17} />
          </button>
        </div>
      </aside>

      <main className="admin-main">
        <header className="admin-topbar">
          <button
            className="admin-menu-button"
            onClick={() => setCollapsed((value) => !value)}
            aria-label="Toggle administrator sidebar"
            title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            <Menu size={20} />
          </button>

          <span className="admin-topbar-label">
            RESEARCH FUNDING &amp; INNOVATION PLATFORM
          </span>

          <div className="admin-topbar-status">
            <i />
            Secure Admin Session
          </div>
        </header>

        <div className="admin-content">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
