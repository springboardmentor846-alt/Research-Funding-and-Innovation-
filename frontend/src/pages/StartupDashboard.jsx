import React from 'react';
import { Rocket, DollarSign, Cpu, ShieldCheck, ArrowUpRight, CheckCircle, Zap } from 'lucide-react';

export const StartupDashboard = ({ onNavigate }) => {
  return (
    <div className="space-y-6">
      {/* Banner */}
      <div className="p-6 rounded-2xl glass-panel bg-gradient-to-r from-slate-900 via-slate-900 to-emerald-950/40 border border-emerald-500/20 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold">
            <Rocket className="w-3.5 h-3.5" />
            <span>Startup Founder Perspective Dashboard</span>
          </div>
          <h2 className="text-2xl font-extrabold text-slate-100 tracking-tight">
            Commercialization & Venture Intelligence
          </h2>
          <p className="text-xs text-slate-400">
            Identify non-dilutive SBIR/STTR grants, accelerator programs, patent licensing opportunities, and technology transfer deals.
          </p>
        </div>

        <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-1">
          <div className="text-[11px] text-slate-400 uppercase font-semibold">Commercialization Readiness</div>
          <div className="text-2xl font-black text-emerald-400">78.4 / 100</div>
          <div className="text-[10px] text-slate-400">Targeting Seed & Phase II SBIR</div>
        </div>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl glass-panel space-y-1">
          <div className="text-[11px] font-semibold text-slate-400 uppercase">Non-Dilutive Grants</div>
          <div className="text-2xl font-bold text-slate-100">$2.5M Available</div>
          <div className="text-[11px] text-emerald-400">Horizon Europe & EIC Accelerator</div>
        </div>
        <div className="p-4 rounded-xl glass-panel space-y-1">
          <div className="text-[11px] font-semibold text-slate-400 uppercase">Tech Opportunities</div>
          <div className="text-2xl font-bold text-cyan-400">8 TRL 5-7 Assets</div>
          <div className="text-[11px] text-slate-400">Ready for Licensing</div>
        </div>
        <div className="p-4 rounded-xl glass-panel space-y-1">
          <div className="text-[11px] font-semibold text-slate-400 uppercase">Competitor Patents Tracked</div>
          <div className="text-2xl font-bold text-purple-400">42 Patents</div>
          <div className="text-[11px] text-slate-400">Zero Freedom-to-Operate Blockers</div>
        </div>
        <div className="p-4 rounded-xl glass-panel space-y-1">
          <div className="text-[11px] font-semibold text-slate-400 uppercase">Accelerator Match</div>
          <div className="text-2xl font-bold text-amber-400">Y Combinator W26</div>
          <div className="text-[11px] text-slate-400">95% Application Fit</div>
        </div>
      </div>

      {/* Sections: Active Venture Opportunities & Commercialization Insights */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="p-5 rounded-xl glass-panel space-y-4">
          <h3 className="text-sm font-bold text-slate-200 flex items-center space-x-2">
            <Zap className="w-4 h-4 text-amber-400" />
            <span>High-Priority Venture & Grant Calls</span>
          </h3>
          <div className="space-y-3">
            <div className="p-3.5 rounded-lg bg-slate-900/80 border border-slate-800 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-100">Horizon Europe DeepTech Catalyst</span>
                <span className="text-xs font-bold text-emerald-400">€2,500,000</span>
              </div>
              <p className="text-xs text-slate-400">Blended grant & equity funding for deeptech hardware scaling.</p>
              <button onClick={() => onNavigate('funding')} className="text-xs text-cyan-400 hover:underline">Apply / Inspect Call</button>
            </div>
            <div className="p-3.5 rounded-lg bg-slate-900/80 border border-slate-800 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-100">Y Combinator Bio & Deep Tech Accelerator</span>
                <span className="text-xs font-bold text-emerald-400">$500,000</span>
              </div>
              <p className="text-xs text-slate-400">3-month intensive scaling program for deep tech spin-outs.</p>
              <button onClick={() => onNavigate('funding')} className="text-xs text-cyan-400 hover:underline">Apply / Inspect Call</button>
            </div>
          </div>
        </div>

        <div className="p-5 rounded-xl glass-panel space-y-4">
          <h3 className="text-sm font-bold text-slate-200 flex items-center space-x-2">
            <Cpu className="w-4 h-4 text-cyan-400" />
            <span>Commercialization Recommendations & Licensing</span>
          </h3>
          <div className="space-y-3 text-xs">
            <div className="p-3.5 rounded-lg bg-slate-900/80 border border-slate-800 space-y-1">
              <div className="font-bold text-slate-200">Productization Roadmap</div>
              <p className="text-slate-400">Initiate pilot customer deployments with corporate drone and edge AI partners.</p>
            </div>
            <div className="p-3.5 rounded-lg bg-slate-900/80 border border-slate-800 space-y-1">
              <div className="font-bold text-slate-200">Technology Transfer Opportunity</div>
              <p className="text-slate-400">Stanford TTO non-exclusive license available for memristor crossbar array patents.</p>
            </div>
            <button onClick={() => onNavigate('scoring')} className="w-full py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 font-bold text-slate-950 transition-colors">
              Run Commercialization Scoring Engine
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
