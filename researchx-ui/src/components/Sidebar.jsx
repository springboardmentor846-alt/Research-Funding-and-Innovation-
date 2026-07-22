import {
  LayoutDashboard,
  FileText,
  Landmark,
  Lightbulb,
  Brain,
  BarChart3,
  Settings,
} from "lucide-react";

import { NavLink, Link } from "react-router-dom";

const menu = [
  {
    icon: LayoutDashboard,
    title: "Dashboard",
    path: "/dashboard",
  },
  {
    icon: FileText,
    title: "Patents",
    path: "/patents",
  },
  {
    icon: Landmark,
    title: "Funding",
    path: "/funding",
  },
  {
    icon: Lightbulb,
    title: "Technologies",
    path: "/technologies",
  },
  {
    icon: Brain,
    title: "AI Insights",
    path: "/ai",
  },
  {
    icon: BarChart3,
    title: "Analytics",
    path: "/analytics",
  },
  {
    icon: Settings,
    title: "Settings",
    path: "/settings",
  },
];

export default function Sidebar() {
  return (
    <aside className="w-72 min-h-screen bg-slate-900 border-r border-slate-800">

      {/* Logo Section */}
      <div className="p-8 border-b border-slate-800">

        <Link to="/" className="block">

          <h1 className="text-3xl font-bold text-cyan-400 hover:text-cyan-300 transition duration-300">
            ResearchX
          </h1>

          <p className="text-slate-400 mt-2 hover:text-white transition duration-300">
            AI Research Platform
          </p>

        </Link>

      </div>

      {/* Menu */}
      <div className="mt-6">

        {menu.map((item, index) => {
          const Icon = item.icon;

          return (
            <NavLink
              key={index}
              to={item.path}
              className={({ isActive }) =>
                `w-full flex items-center gap-4 px-8 py-4 transition-all duration-300 ${
                  isActive
                    ? "bg-cyan-600 text-white"
                    : "text-slate-300 hover:bg-cyan-600 hover:text-white"
                }`
              }
            >
              <Icon size={22} />

              <span className="text-lg">
                {item.title}
              </span>

            </NavLink>
          );
        })}

      </div>

    </aside>
  );
}