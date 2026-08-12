import React from 'react';
import { 
  Award, BookOpen, ShieldCheck, Sparkles, TrendingUp, DollarSign, 
  ExternalLink, ArrowUpRight, CheckCircle2 
} from 'lucide-react';

export const ResearcherDashboard = ({ onNavigate }) => {
  const recommendations = [
    {
      id: 'grant-1',
      title: 'NSF AI & Quantum Information Systems Convergence Grant',
      agency: 'National Science Foundation (NSF)',
      amount: '$1,500,000',
      matchScore: 92.5,
      deadline: 'In 45 Days',
      type: 'Government Grant'
    },
    {
      id: 'grant-2',
      title: 'ARPA-E Next-Gen Solid-State Battery Fund',
      agency: 'ARPA-E',
      amount: '$2,000,000',
      matchScore: 88.0,
      deadline: 'In 20 Days',
      type: 'Research Council'
    },
    {
      id: 'grant-3',
      title: 'NIH Genomic Medicine & Precision Therapeutics Grant',
      agency: 'NIH',
      amount: '$1,200,000',
      matchScore: 84.5,
      deadline: 'In 110 Days',
      type: 'Government Grant'
    }
  ];

  const trends = [
    { topic: 'Neuromorphic Edge AI Chips', growth: '+148.5%', hotspot: 94.2, stage: 'Emerging' },
    { topic: 'Quantum Graph Neural Networks', growth: '+185.2%', hotspot: 91.8, stage: 'Emerging' },
    { topic: 'Solid-State Lithium Metal Batteries', growth: '+76.4%', hotspot: 86.5, stage: 'Growing' }
  ];

  return (
    <div className="space-y-6">
      {/* Welcome & Innovation Score Banner */}
      <div className="p-6 rounded-2xl glass-panel bg-gradient-to-r from-slate-900 via-slate-900 to-cyan-950/40 border border-cyan-500/20 relative overflow-hidden">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2 max-w-xl">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-semibold">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Researcher Perspective Dashboard</span>
            </div>
            <h2 className="text-2xl font-extrabold text-slate-100 tracking-tight">
              Welcome back, Dr. Aris Thorne
            </h2>
            <p className="text-xs text-slate-400 leading-relaxed">
              Your research profile is matched with 14 active funding opportunities across NSF, NIH, and Horizon Europe.
            </p>
          </div>

          <div className="flex items-center space-x-4 bg-slate-950/80 p-4 rounded-xl border border-slate-800">
            <div className="w-14 h-14 rounded-full bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center text-slate-950 font-black text-xl shadow-lg shadow-cyan-500/20">
              86.3
            </div>
            <div>
              <div className="text-xs font-bold text-slate-300">Composite Innovation Score</div>
              <div className="text-[11px] text-cyan-400">Top 5% in AI & Neuromorphic Hardware</div>
              <button 
                onClick={() => onNavigate('scoring')}
                className="mt-1 text-[11px] text-slate-400 hover:text-cyan-300 underline flex items-center space-x-1"
              >
                <span>Recalculate Score</span>
                <ArrowUpRight className="w-3 h-3" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl glass-panel space-y-1">
          <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Matched Grants</div>
          <div className="text-2xl font-bold text-slate-100">14 Active</div>
          <div className="text-[11px] text-emerald-400 font-medium">3 Closing this month</div>
        </div>
        <div className="p-4 rounded-xl glass-panel space-y-1">
          <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Indexed Publications</div>
          <div className="text-2xl font-bold text-slate-100">18 Papers</div>
          <div className="text-[11px] text-cyan-400 font-medium">840 Total Citations (h-index: 14)</div>
        </div>
        <div className="p-4 rounded-xl glass-panel space-y-1">
          <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Patents & IP Claims</div>
          <div className="text-2xl font-bold text-slate-100">3 Granted</div>
          <div className="text-[11px] text-purple-400 font-medium">IPC Classification: G06N 3/063</div>
        </div>
        <div className="p-4 rounded-xl glass-panel space-y-1">
          <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Research Hotspot Rank</div>
          <div className="text-2xl font-bold text-cyan-400">#1 Top 1%</div>
          <div className="text-[11px] text-slate-400 font-medium">Neuromorphic Edge AI</div>
        </div>
      </div>

      {/* Recommended Funding Opportunities */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-bold text-slate-200 flex items-center space-x-2">
            <DollarSign className="w-4 h-4 text-emerald-400" />
            <span>AI-Matched Funding Opportunities</span>
          </h3>
          <button 
            onClick={() => onNavigate('funding')}
            className="text-xs text-cyan-400 hover:text-cyan-300 font-medium flex items-center space-x-1"
          >
            <span>View All Grants</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {recommendations.map(grant => (
            <div key={grant.id} className="p-5 rounded-xl glass-panel glass-panel-hover flex flex-col justify-between space-y-4">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="px-2.5 py-0.5 rounded-md bg-emerald-500/10 text-emerald-400 text-[10px] font-bold border border-emerald-500/30">
                    {grant.matchScore}% Eligibility Match
                  </span>
                  <span className="text-[11px] text-slate-400">{grant.deadline}</span>
                </div>
                <h4 className="text-sm font-bold text-slate-100 line-clamp-2 leading-snug">{grant.title}</h4>
                <p className="text-xs text-slate-400 font-medium">{grant.agency}</p>
              </div>

              <div className="pt-3 border-t border-slate-800 flex items-center justify-between">
                <div>
                  <div className="text-[10px] text-slate-500 uppercase font-semibold">Award Up To</div>
                  <div className="text-sm font-bold text-slate-200">{grant.amount}</div>
                </div>
                <button 
                  onClick={() => onNavigate('funding')}
                  className="px-3 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold transition-colors"
                >
                  Inspect Grant
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Research Trends & Citation Insights */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="p-5 rounded-xl glass-panel space-y-4">
          <h3 className="text-sm font-bold text-slate-200 flex items-center space-x-2">
            <TrendingUp className="w-4 h-4 text-cyan-400" />
            <span>Emerging Research Hotspots in Your Domain</span>
          </h3>
          <div className="space-y-3">
            {trends.map((t, idx) => (
              <div key={idx} className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 flex items-center justify-between">
                <div>
                  <div className="text-xs font-bold text-slate-200">{t.topic}</div>
                  <div className="text-[11px] text-slate-400">Growth Velocity: <span className="text-emerald-400 font-semibold">{t.growth}</span></div>
                </div>
                <div className="text-right">
                  <div className="text-xs font-bold text-cyan-400">{t.hotspot}/100</div>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-300">{t.stage}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="p-5 rounded-xl glass-panel space-y-4">
          <h3 className="text-sm font-bold text-slate-200 flex items-center space-x-2">
            <ShieldCheck className="w-4 h-4 text-purple-400" />
            <span>Intellectual Property & Citation Highlights</span>
          </h3>
          <div className="space-y-3 text-xs text-slate-300">
            <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 space-y-1">
              <div className="flex items-center justify-between font-bold text-slate-100">
                <span>Patent US-11894562-B2</span>
                <span className="text-purple-400 text-[11px]">48 Citations</span>
              </div>
              <p className="text-slate-400 text-[11px]">Neuromorphic Crossbar Circuit Architecture with On-Chip Spike Training</p>
            </div>
            <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 space-y-1">
              <div className="flex items-center justify-between font-bold text-slate-100">
                <span>Nature Electronics Publication</span>
                <span className="text-cyan-400 text-[11px]">142 Citations</span>
              </div>
              <p className="text-slate-400 text-[11px]">Scalable Neuromorphic Computing via Spike-Timing-Dependent Plasticity</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
