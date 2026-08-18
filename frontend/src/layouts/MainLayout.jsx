import React, { useState } from "react";
import { NavLink, Outlet, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import NotificationBell from "../components/NotificationBell.jsx";

const navItems = [
  { to: "/dashboard", label: "Dashboard", icon: "📊" },
  { to: "/publications", label: "Publications", icon: "📄" },
  { to: "/funding", label: "Funding", icon: "💰" },
  { to: "/recommendations", label: "AI Recommendations", icon: "🎯" },
  { to: "/patents", label: "Patents", icon: "🔬" },
  { to: "/patents/analytics", label: "Patent Analytics", icon: "📊" },
  { to: "/saved-patents", label: "Saved Patents", icon: "⭐" },
  { to: "/trends", label: "Trends", icon: "📈" },
  { to: "/ai-assistant", label: "AI Assistant", icon: "🤖" },
  { to: "/search", label: "Search", icon: "🔍" },
  { to: "/profile", label: "Profile", icon: "👤" },
];

export default function MainLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <div className="flex h-screen bg-slate-50">
      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        } lg:translate-x-0 fixed lg:static inset-y-0 left-0 z-30 w-64 bg-slate-900 text-slate-100 transition-transform duration-200 flex flex-col`}
      >
        <div className="px-6 py-5 border-b border-slate-800">
          <div className="flex items-center space-x-2">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center text-white font-bold">
              R
            </div>
            <div>
              <div className="font-bold text-sm">Research Platform</div>
              <div className="text-xs text-slate-400">AI-Powered</div>
            </div>
          </div>
        </div>

        <nav className="flex-1 overflow-y-auto py-4">
          <div className="px-4 space-y-1">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={() => setSidebarOpen(false)}
                className={({ isActive }) =>
                  `flex items-center space-x-3 px-3 py-2 rounded-lg text-sm transition ${
                    isActive
                      ? "bg-primary-600 text-white"
                      : "text-slate-300 hover:bg-slate-800 hover:text-white"
                  }`
                }
              >
                <span className="text-base">{item.icon}</span>
                <span>{item.label}</span>
              </NavLink>
            ))}
            {user?.role === "admin" && (
              <NavLink
                to="/admin"
                onClick={() => setSidebarOpen(false)}
                className={({ isActive }) =>
                  `flex items-center space-x-3 px-3 py-2 rounded-lg text-sm transition ${
                    isActive
                      ? "bg-red-600 text-white"
                      : "text-slate-300 hover:bg-slate-800 hover:text-white"
                  }`
                }
              >
                <span className="text-base">🛡️</span>
                <span>Open Admin Portal</span>
              </NavLink>
            )}
          </div>
        </nav>

        <div className="px-4 py-4 border-t border-slate-800">
          <div className="flex items-center space-x-3 mb-3">
            <div className="w-9 h-9 rounded-full bg-primary-500 flex items-center justify-center text-white font-bold text-sm">
              {(user?.full_name || user?.username || "U").charAt(0).toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium truncate">{user?.full_name || user?.username}</div>
              <div className="text-xs text-slate-400 capitalize truncate">{user?.role?.replace("_", " ")}</div>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="w-full text-left text-sm text-slate-400 hover:text-white py-1.5 px-2 rounded hover:bg-slate-800"
          >
            ↪ Logout
          </button>
        </div>
      </aside>

      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black/50 z-20"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="bg-white border-b border-slate-200 px-4 lg:px-8 py-4 flex items-center justify-between flex-shrink-0">
          <button
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden text-slate-600"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <h1 className="text-lg font-semibold text-slate-800 capitalize">
            {location.pathname.replace("/", "") || "Dashboard"}
          </h1>
          <div className="flex items-center gap-3">
            <NotificationBell />
            <div className="text-sm text-slate-500 hidden sm:block">
              Welcome, <span className="font-medium text-slate-700">{user?.full_name || user?.username}</span>
            </div>
          </div>
        </header>
        <main className="flex-1 overflow-y-auto p-4 lg:p-8 animate-fade-in">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
