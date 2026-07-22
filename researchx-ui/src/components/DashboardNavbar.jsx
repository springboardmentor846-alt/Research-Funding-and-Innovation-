import { Bell, User } from "lucide-react";

export default function DashboardNavbar() {
  return (
    <nav className="bg-slate-900 border-b border-slate-800 px-8 py-5 flex justify-between items-center">

      <div>
        <h1 className="text-3xl font-bold text-cyan-400">
          ResearchX Dashboard
        </h1>

        <p className="text-slate-400">
          AI Powered Research Intelligence
        </p>
      </div>

      <div className="flex gap-5 items-center">

        <Bell className="text-white cursor-pointer" />

        <User className="text-white cursor-pointer" />

      </div>

    </nav>
  );
}