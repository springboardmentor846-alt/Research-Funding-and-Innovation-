import React, { useState } from "react";
import { NavLink, Outlet, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

/**
 * Admin Portal layout.
 *
 * Completely separate navigation from the researcher-facing MainLayout:
 *   - Distinct dark sidebar with admin-only sections.
 *   - No links to researcher-only features (Apply for Funding, My
 *     Applications, AI Recommendations for the admin user, etc.).
 *   - The admin never sees an "Apply" button or any researcher workflow.
 */
const navSections = [
  {
    label: "Overview",
    items: [
      { to: "/admin", label: "Dashboard", icon: "📊", end: true },
    ],
  },
  {
    label: "Management",
    items: [
      { to: "/admin/users", label: "Users", icon: "👥" },
      { to: "/admin/funding-intel", label: "Funding Intel", icon: "🛰" },
      { to: "/admin/funding", label: "Imported Funding", icon: "💰" },
      { to: "/admin/publications", label: "Publications", icon: "📄" },
      { to: "/admin/patents", label: "Patents", icon: "🔬" },
      { to: "/admin/patents-intel", label: "Patent Intelligence", icon: "🛰️" },
    ],
  },
  {
    label: "Intelligence",
    items: [
      { to: "/admin/recommendations", label: "AI Recommendations", icon: "🎯" },
      { to: "/admin/reports", label: "Reports & Analytics", icon: "📈" },
    ],
  },
  {
    label: "System",
    items: [
      { to: "/admin/settings", label: "Settings", icon: "⚙️" },
    ],
  },
];

export default function AdminLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  function handleLogout() {
    logout();
    navigate("/login");
  }

  // Pick a useful title from the current pathname
  const currentTitle = deriveTitle(location.pathname);

  return (
    <div className="flex h-screen bg-slate-50">
      <aside
        className={`${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        } lg:translate-x-0 fixed lg:static inset-y-0 left-0 z-30 w-64 bg-slate-900 text-slate-100 transition-transform duration-200 flex flex-col`}
      >
        <div className="px-6 py-5 border-b border-slate-800">
          <div className="flex items-center space-x-2">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-red-500 to-amber-500 flex items-center justify-center text-white font-bold">
              A
            </div>
            <div>
              <div className="font-bold text-sm">Admin Portal</div>
              <div className="text-xs text-slate-400">Platform Management</div>
            </div>
          </div>
        </div>

        <nav className="flex-1 overflow-y-auto py-4">
          {navSections.map((section) => (
            <div key={section.label} className="px-4 mb-4">
              <div className="px-3 mb-2 text-[10px] uppercase tracking-wider text-slate-500 font-semibold">
                {section.label}
              </div>
              <div className="space-y-1">
                {section.items.map((item) => (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    end={item.end}
                    onClick={() => setSidebarOpen(false)}
                    className={({ isActive }) =>
                      `flex items-center space-x-3 px-3 py-2 rounded-lg text-sm transition ${
                        isActive
                          ? "bg-red-600 text-white"
                          : "text-slate-300 hover:bg-slate-800 hover:text-white"
                      }`
                    }
                  >
                    <span className="text-base">{item.icon}</span>
                    <span>{item.label}</span>
                  </NavLink>
                ))}
              </div>
            </div>
          ))}
        </nav>

        <div className="px-4 py-4 border-t border-slate-800">
          <div className="flex items-center space-x-3 mb-3">
            <div className="w-9 h-9 rounded-full bg-red-500 flex items-center justify-center text-white font-bold text-sm">
              {(user?.full_name || user?.username || "A").charAt(0).toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium truncate">{user?.full_name || user?.username}</div>
              <div className="text-xs text-slate-400 truncate">Administrator</div>
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => navigate("/dashboard")}
              className="flex-1 text-left text-xs text-slate-400 hover:text-white py-1.5 px-2 rounded hover:bg-slate-800"
            >
              ↗ User View
            </button>
            <button
              onClick={handleLogout}
              className="flex-1 text-left text-xs text-slate-400 hover:text-white py-1.5 px-2 rounded hover:bg-slate-800"
            >
              ↪ Logout
            </button>
          </div>
        </div>
      </aside>

      {sidebarOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black/50 z-20"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="bg-white border-b border-slate-200 px-4 lg:px-8 py-4 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden text-slate-600"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <h1 className="text-lg font-semibold text-slate-800">{currentTitle}</h1>
          </div>
          <div className="text-sm text-slate-500 hidden sm:block">
            Signed in as{" "}
            <span className="font-medium text-slate-700">{user?.full_name || user?.username}</span>
            <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
              Admin
            </span>
          </div>
        </header>
        <main className="flex-1 overflow-y-auto p-4 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

function deriveTitle(pathname) {
  if (pathname === "/admin" || pathname === "/admin/") return "Dashboard";
  const seg = pathname.replace("/admin/", "").split("/")[0];
  const map = {
    users: "User Management",
    funding: "Imported Funding",
    "funding-intel": "Funding Intelligence",
    publications: "Publication Monitoring",
    patents: "Patent Monitoring",
    "patents-intel": "Patent Intelligence",
    recommendations: "AI Recommendation Monitoring",
    reports: "Reports & Analytics",
    settings: "System Settings",
  };
  return map[seg] || "Admin Portal";
}
