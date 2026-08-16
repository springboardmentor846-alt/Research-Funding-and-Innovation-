import React, { useState } from 'react';
import { Navbar } from '../components/common/Navbar';
import { Sidebar } from '../components/common/Sidebar';
import { Footer } from '../components/common/Footer';
import { useAuth } from '../contexts/AuthContext';
import { userAPI } from '../services/api';
import { Settings, User, Key, Shield, Save } from 'lucide-react';

export const SettingsPage = () => {
  const { user, updateUser } = useAuth();
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [org, setOrg] = useState(user?.organization || '');
  const [msg, setMsg] = useState('');

  const handleUpdate = async (e) => {
    e.preventDefault();
    try {
      await userAPI.updateMe({ full_name: fullName, organization: org });
      updateUser({ full_name: fullName, organization: org });
      setMsg('Account settings updated successfully!');
    } catch (e) {
      setMsg('Failed to update account settings.');
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
      <Navbar />
      <div className="flex-1 flex">
        <Sidebar />
        <main className="flex-1 p-8 space-y-8 overflow-y-auto">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight gradient-text">
              User & Security Settings
            </h1>
            <p className="text-sm text-slate-400 mt-1">Manage personal credentials, security keys, and organization metadata.</p>
          </div>

          <form onSubmit={handleUpdate} className="glass-card p-8 max-w-2xl space-y-6">
            {msg && <div className="p-3 bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 rounded-xl text-sm">{msg}</div>}

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Full Name</label>
                <input type="text" value={fullName} onChange={(e) => setFullName(e.target.value)} className="w-full p-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm" />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Email Address</label>
                <input type="email" disabled value={user?.email || ''} className="w-full p-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-sm text-slate-500 cursor-not-allowed" />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Organization</label>
                <input type="text" value={org} onChange={(e) => setOrg(e.target.value)} className="w-full p-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm" />
              </div>
            </div>

            <button type="submit" className="px-6 py-3 rounded-xl font-bold text-white gradient-bg-accent shadow-lg flex items-center space-x-2">
              <Save className="w-4 h-4" />
              <span>Save Account Settings</span>
            </button>
          </form>
        </main>
      </div>
      <Footer />
    </div>
  );
};
