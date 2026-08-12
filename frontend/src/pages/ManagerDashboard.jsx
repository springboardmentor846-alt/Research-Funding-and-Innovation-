import React from 'react';
import { Briefcase, BarChart3, PieChart, Layers, TrendingUp, DollarSign } from 'lucide-react';

export const ManagerDashboard = ({ onNavigate }) => {
  return (
    <div className="space-y-6">
      {/* Banner */}
      <div className="p-6 rounded-2xl glass-panel bg-gradient-to-r from-slate-900 via-slate-900 to-amber-950/40 border border-amber-500/20 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-semibold">
            <Briefcase className="w-3.5 h-3.5" />
            <span>Innovation Manager Perspective Dashboard</span>
          </div>
          <h2 className="text-2xl font-extrabold text-slate-100 tracking-tight">
            Institutional R&D Portfolio & Pipeline Tracking
          </h2>
          <p className="text-xs text-slate-400">
            Monitor technology transfer pipelines, university R&D portfolios, grant success rates, and cross-departmental trend velocity.
          </p>
        </div>

        <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-1">
          <div className="text-[11px] text-slate-400 uppercase font-semibold">Total Tracked Funding</div>
          <div className="text-2xl font-black text-amber-400">$14.25M</div>
          <div className="text-[10px] text-emerald-400">65.3% Grant Success Rate</div>
        </div>
      </div>

      {/* Pipeline Stage Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl glass-panel space-y-1">
          <div className="text-[11px] font-semibold text-slate-400 uppercase">Stage 1: Ideation</div>
          <div className="text-2xl font-bold text-slate-200">8 Projects</div>
          <div className="text-[11px] text-slate-500">TRL 1-2 Basic Principles</div>
        </div>
        <div className="p-4 rounded-xl glass-panel space-y-1">
          <div className="text-[11px] font-semibold text-slate-400 uppercase">Stage 2: Lab Proof</div>
          <div className="text-2xl font-bold text-cyan-400">10 Projects</div>
          <div className="text-[11px] text-slate-500">TRL 3-4 Validation</div>
        </div>
        <div className="p-4 rounded-xl glass-panel space-y-1">
          <div className="text-[11px] font-semibold text-slate-400 uppercase">Stage 3: Prototype</div>
          <div className="text-2xl font-bold text-amber-400">6 Projects</div>
          <div className="text-[11px] text-slate-500">TRL 5-6 Pilot Ready</div>
        </div>
        <div className="p-4 rounded-xl glass-panel space-y-1">
          <div className="text-[11px] font-semibold text-slate-400 uppercase">Stage 4: Spin-Out / License</div>
          <div className="text-2xl font-bold text-emerald-400">4 Projects</div>
          <div className="text-[11px] text-slate-500">TRL 7+ Market Ready</div>
        </div>
      </div>

      {/* Portfolio Table */}
      <div className="p-5 rounded-xl glass-panel space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-200 flex items-center space-x-2">
            <BarChart3 className="w-4 h-4 text-amber-400" />
            <span>Active Innovation Pipeline Projects</span>
          </h3>
          <button onClick={() => onNavigate('scoring')} className="text-xs text-amber-400 hover:underline font-semibold">
            Evaluate New Project
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/80 text-slate-400 border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-3">Project Title</th>
                <th className="py-2.5 px-3">Domain</th>
                <th className="py-2.5 px-3">Innovation Score</th>
                <th className="py-2.5 px-3">TRL Level</th>
                <th className="py-2.5 px-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              <tr>
                <td className="py-3 px-3 font-semibold text-slate-100">Neuromorphic Edge AI Processor</td>
                <td className="py-3 px-3">Artificial Intelligence</td>
                <td className="py-3 px-3"><span className="text-emerald-400 font-bold">86.3</span> / 100</td>
                <td className="py-3 px-3">TRL 6 (Pilot)</td>
                <td className="py-3 px-3"><span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">Spin-Out Ready</span></td>
              </tr>
              <tr>
                <td className="py-3 px-3 font-semibold text-slate-100">Quantum Graph Neural Networks</td>
                <td className="py-3 px-3">Quantum Computing</td>
                <td className="py-3 px-3"><span className="text-cyan-400 font-bold">81.5</span> / 100</td>
                <td className="py-3 px-3">TRL 4 (Lab)</td>
                <td className="py-3 px-3"><span className="px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">NSF Grant Pending</span></td>
              </tr>
              <tr>
                <td className="py-3 px-3 font-semibold text-slate-100">Solid-State Lithium Metal Batteries</td>
                <td className="py-3 px-3">Clean Energy</td>
                <td className="py-3 px-3"><span className="text-amber-400 font-bold">88.2</span> / 100</td>
                <td className="py-3 px-3">TRL 7 (Commercial)</td>
                <td className="py-3 px-3"><span className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30">JDA Active</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
