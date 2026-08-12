import React from 'react';
import { Settings, Users, Database, ShieldCheck, Activity, Cpu } from 'lucide-react';

export const AdminDashboard = ({ onNavigate }) => {
  return (
    <div className="space-y-6">
      {/* Banner */}
      <div className="p-6 rounded-2xl glass-panel bg-gradient-to-r from-slate-900 via-slate-900 to-purple-950/40 border border-purple-500/20 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-400 text-xs font-semibold">
            <Settings className="w-3.5 h-3.5" />
            <span>Administrator Perspective Dashboard</span>
          </div>
          <h2 className="text-2xl font-extrabold text-slate-100 tracking-tight">
            System Administration & Platform Metrics
          </h2>
          <p className="text-xs text-slate-400">
            Manage user roles, platform data ingestion (OpenAlex, CrossRef, USPTO), system health, and API latency.
          </p>
        </div>

        <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-1">
          <div className="text-[11px] text-slate-400 uppercase font-semibold">System Health</div>
          <div className="text-2xl font-black text-emerald-400">100% OPERATIONAL</div>
          <div className="text-[10px] text-slate-400">API Latency: 42ms</div>
        </div>
      </div>

      {/* Admin Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl glass-panel space-y-1">
          <div className="text-[11px] font-semibold text-slate-400 uppercase">Registered Users</div>
          <div className="text-2xl font-bold text-slate-100">4 Active Users</div>
          <div className="text-[11px] text-purple-400 font-medium">4 Roles Configured</div>
        </div>
        <div className="p-4 rounded-xl glass-panel space-y-1">
          <div className="text-[11px] font-semibold text-slate-400 uppercase">Grants Indexed</div>
          <div className="text-2xl font-bold text-emerald-400">5 Active Calls</div>
          <div className="text-[11px] text-slate-400">$32.0M Total Value</div>
        </div>
        <div className="p-4 rounded-xl glass-panel space-y-1">
          <div className="text-[11px] font-semibold text-slate-400 uppercase">Patents Harvested</div>
          <div className="text-2xl font-bold text-cyan-400">3 Patents</div>
          <div className="text-[11px] text-slate-400">USPTO & Google Patents</div>
        </div>
        <div className="p-4 rounded-xl glass-panel space-y-1">
          <div className="text-[11px] font-semibold text-slate-400 uppercase">Publications Synced</div>
          <div className="text-2xl font-bold text-amber-400">3 Papers</div>
          <div className="text-[11px] text-slate-400">OpenAlex API Live</div>
        </div>
      </div>

      {/* Role Distribution & Data Ingestion Logs */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="p-5 rounded-xl glass-panel space-y-4">
          <h3 className="text-sm font-bold text-slate-200 flex items-center space-x-2">
            <Users className="w-4 h-4 text-purple-400" />
            <span>Role-Based Access Control Breakdown</span>
          </h3>
          <div className="space-y-2 text-xs">
            <div className="flex justify-between p-2.5 rounded bg-slate-900 border border-slate-800">
              <span className="text-slate-300">RESEARCHER</span>
              <span className="font-bold text-cyan-400">1 User (dr.thorne@stanford.edu)</span>
            </div>
            <div className="flex justify-between p-2.5 rounded bg-slate-900 border border-slate-800">
              <span className="text-slate-300">STARTUP_FOUNDER</span>
              <span className="font-bold text-emerald-400">1 User (elena@startup.io)</span>
            </div>
            <div className="flex justify-between p-2.5 rounded bg-slate-900 border border-slate-800">
              <span className="text-slate-300">INNOVATION_MANAGER</span>
              <span className="font-bold text-amber-400">1 User (m.brody@tto.edu)</span>
            </div>
            <div className="flex justify-between p-2.5 rounded bg-slate-900 border border-slate-800">
              <span className="text-slate-300">SYSTEM_ADMIN</span>
              <span className="font-bold text-purple-400">1 User (admin@platform.gov)</span>
            </div>
          </div>
        </div>

        <div className="p-5 rounded-xl glass-panel space-y-4">
          <h3 className="text-sm font-bold text-slate-200 flex items-center space-x-2">
            <Database className="w-4 h-4 text-cyan-400" />
            <span>Data Ingestion & Pipeline Health</span>
          </h3>
          <div className="space-y-2 text-xs text-slate-300">
            <div className="p-2.5 rounded bg-slate-900 border border-slate-800 flex justify-between">
              <span>OpenAlex API Connector</span>
              <span className="text-emerald-400 font-bold">200 OK (Synced 10m ago)</span>
            </div>
            <div className="p-2.5 rounded bg-slate-900 border border-slate-800 flex justify-between">
              <span>USPTO Patent Feed</span>
              <span className="text-emerald-400 font-bold">200 OK (Synced 1h ago)</span>
            </div>
            <div className="p-2.5 rounded bg-slate-900 border border-slate-800 flex justify-between">
              <span>Vector Database (Qdrant/FAISS)</span>
              <span className="text-emerald-400 font-bold">ONLINE (1,420 Embeddings)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
