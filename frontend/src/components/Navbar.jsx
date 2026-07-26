import { Bell, User } from "lucide-react";
import { useAuth } from "@/context/AuthContext";

export default function Navbar() {
  const { user } = useAuth();

  return (
    <header className="h-14 bg-white border-b border-slate-200 flex items-center justify-between px-6 shrink-0">
      <h1 className="text-sm font-semibold text-slate-700 tracking-wide">
        Research Funding &amp; Innovation Intelligence Platform
      </h1>
      <div className="flex items-center gap-4">
        <button className="text-slate-500 hover:text-slate-700">
          <Bell size={18} />
        </button>
        <div className="flex items-center gap-2 text-sm text-slate-700">
          <div className="w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center text-white">
            <User size={14} />
          </div>
          <span className="font-medium">{user?.name || user?.email || "User"}</span>
          <span className="text-xs text-slate-400 capitalize">({user?.role || "researcher"})</span>
        </div>
      </div>
    </header>
  );
}
