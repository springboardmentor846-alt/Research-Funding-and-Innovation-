import { Bell, Search, UserCircle2, Home } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function Header({
  title = "Dashboard",
  subtitle = "Welcome back! Here's your research overview.",
}) {
  const navigate = useNavigate();

  return (
    <header className="flex justify-between items-center mb-8">

      <div>
        <h1 className="text-4xl font-bold text-white">
          {title}
        </h1>

        <p className="text-slate-400 mt-2">
          {subtitle}
        </p>
      </div>

      <div className="flex items-center gap-4">

        {/* Home Button */}
        <button
          onClick={() => navigate("/")}
          className="bg-slate-900 p-3 rounded-xl border border-slate-700 hover:border-cyan-400 transition"
        >
          <Home className="text-white" size={20} />
        </button>

        {/* Search */}
        <div className="bg-slate-900 rounded-xl px-4 py-3 flex items-center gap-3 border border-slate-700">

          <Search size={18} className="text-slate-400"/>

          <input
            type="text"
            placeholder="Search..."
            className="bg-transparent outline-none text-white placeholder:text-slate-500 w-52"
          />

        </div>

        {/* Notifications */}
        <button className="bg-slate-900 p-3 rounded-xl border border-slate-700 hover:border-cyan-400 transition">
          <Bell className="text-white"/>
        </button>

        {/* Profile */}
        <button className="bg-cyan-500 p-2 rounded-full">
          <UserCircle2 size={34} className="text-white"/>
        </button>

      </div>

    </header>
  );
}