import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  LayoutDashboard, DollarSign, Star, ShieldCheck,
  BookOpen, BarChart2, User, LogOut,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/context/AuthContext";

const navItems = [
  { to: "/dashboard",            icon: LayoutDashboard, label: "Dashboard" },
  { to: "/funding",              icon: DollarSign,      label: "Funding" },
  { to: "/recommendations",      icon: Star,            label: "Recommendations" },
  { to: "/grant-matching",       icon: ShieldCheck,     label: "Grant Matching" },
  { to: "/research-dashboard",   icon: BarChart2,       label: "Research Intel" },
  { to: "/publications",         icon: BookOpen,        label: "Publications" },
  { to: "/my-publications",      icon: BookOpen,        label: "My Publications" },
  { to: "/profile",              icon: User,            label: "Profile" },
];

export default function Sidebar() {
  const { pathname } = useLocation();
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <aside className="w-56 min-h-screen bg-slate-900 text-white flex flex-col shrink-0">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-slate-700">
        <p className="text-xs font-semibold text-slate-400 uppercase tracking-widest">Platform</p>
        <h2 className="text-base font-bold mt-0.5 leading-tight">Research Funding</h2>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-0.5">
        {navItems.map(({ to, icon: Icon, label }) => (
          <Link
            key={to}
            to={to}
            className={cn(
              "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
              pathname === to
                ? "bg-blue-600 text-white"
                : "text-slate-300 hover:bg-slate-800 hover:text-white"
            )}
          >
            <Icon size={17} />
            {label}
          </Link>
        ))}
      </nav>

      {/* Logout */}
      <div className="px-3 py-4 border-t border-slate-700">
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-slate-300 hover:bg-slate-800 hover:text-white w-full transition-colors"
        >
          <LogOut size={17} />
          Logout
        </button>
      </div>
    </aside>
  );
}
