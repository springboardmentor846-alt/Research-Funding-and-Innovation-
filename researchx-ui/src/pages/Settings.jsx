import Sidebar from "../components/Sidebar";
import Header from "../components/Header";
import { User, Bell, Moon, Shield } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function SettingsPage() {
  const navigate = useNavigate();

  const handleLogout = () => {
    // Remove login status
    localStorage.removeItem("isLoggedIn");

    // Redirect to Landing Page
    navigate("/");
  };

  return (
    <div className="flex bg-slate-950 min-h-screen">

      <Sidebar />

      <main className="flex-1 p-8 overflow-auto">

        <Header
          title="Settings"
          subtitle="Manage your ResearchX preferences."
        />

        <div className="space-y-8">

          {/* Profile Settings */}
          <div className="bg-slate-900 border border-slate-700 rounded-2xl p-6">

            <div className="flex items-center gap-3 mb-6">
              <User className="text-cyan-400" />
              <h2 className="text-2xl font-bold text-white">
                Profile Settings
              </h2>
            </div>

            <div className="grid md:grid-cols-2 gap-6">

              <div>
                <label className="text-slate-400">Full Name</label>
                <input
                  type="text"
                  defaultValue="Sravani Gembali"
                  className="mt-2 w-full bg-slate-800 border border-slate-700 rounded-lg p-3 text-white"
                />
              </div>

              <div>
                <label className="text-slate-400">Email</label>
                <input
                  type="email"
                  defaultValue="sravani@email.com"
                  className="mt-2 w-full bg-slate-800 border border-slate-700 rounded-lg p-3 text-white"
                />
              </div>

              <div>
                <label className="text-slate-400">Organization</label>
                <input
                  type="text"
                  defaultValue="PVPSIT"
                  className="mt-2 w-full bg-slate-800 border border-slate-700 rounded-lg p-3 text-white"
                />
              </div>

              <div>
                <label className="text-slate-400">Research Domain</label>
                <input
                  type="text"
                  defaultValue="Artificial Intelligence"
                  className="mt-2 w-full bg-slate-800 border border-slate-700 rounded-lg p-3 text-white"
                />
              </div>

            </div>

          </div>

          {/* Notifications */}
          <div className="bg-slate-900 border border-slate-700 rounded-2xl p-6">

            <div className="flex items-center gap-3 mb-6">
              <Bell className="text-yellow-400" />
              <h2 className="text-2xl font-bold text-white">
                Notifications
              </h2>
            </div>

            <div className="space-y-4 text-white">

              <label className="flex items-center gap-3">
                <input type="checkbox" defaultChecked />
                Funding Alerts
              </label>

              <label className="flex items-center gap-3">
                <input type="checkbox" defaultChecked />
                Patent Updates
              </label>

              <label className="flex items-center gap-3">
                <input type="checkbox" defaultChecked />
                Technology News
              </label>

            </div>

          </div>

          {/* Appearance */}
          <div className="bg-slate-900 border border-slate-700 rounded-2xl p-6">

            <div className="flex items-center gap-3 mb-6">
              <Moon className="text-purple-400" />
              <h2 className="text-2xl font-bold text-white">
                Appearance
              </h2>
            </div>

            <div className="flex justify-between items-center">

              <p className="text-white">
                Dark Theme
              </p>

              <button className="bg-cyan-500 text-black px-5 py-2 rounded-lg font-semibold">
                Enabled
              </button>

            </div>

          </div>

          {/* Security */}
          <div className="bg-slate-900 border border-slate-700 rounded-2xl p-6">

            <div className="flex items-center gap-3 mb-6">
              <Shield className="text-red-400" />
              <h2 className="text-2xl font-bold text-white">
                Security
              </h2>
            </div>

            <div className="flex gap-4">

              <button className="bg-cyan-500 hover:bg-cyan-600 text-black px-6 py-3 rounded-xl font-semibold">
                Change Password
              </button>

              <button
                onClick={handleLogout}
                className="bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-xl font-semibold"
              >
                Logout
              </button>

            </div>

          </div>

          {/* Save Button */}
          <div className="flex justify-end">

            <button className="bg-green-500 hover:bg-green-600 text-black px-8 py-3 rounded-xl font-bold">
              Save Changes
            </button>

          </div>

        </div>

      </main>

    </div>
  );
}