import React from 'react';
import { Cpu, CheckCircle2, Circle, Activity, ArrowRight, Zap } from 'lucide-react';

export const TechnologyIntelligence = () => {
  const technologies = [
    {
      name: 'Neuromorphic Edge AI Chips',
      domain: 'Artificial Intelligence',
      trl: 6,
      stage: 'Pilot',
      score: 78.5,
      density: 'High',
      innovators: ['Stanford', 'Intel Labs', 'SynSense', 'BrainChip'],
      patents: 340,
      funding: '$450,000,000'
    },
    {
      name: 'Quantum Machine Learning (QML)',
      domain: 'Quantum Computing',
      trl: 4,
      stage: 'R&D',
      score: 52.0,
      density: 'Medium',
      innovators: ['Google Quantum AI', 'IBM Quantum', 'Rigetti'],
      patents: 120,
      funding: '$280,000,000'
    },
    {
      name: 'Solid-State Lithium Metal Batteries',
      domain: 'Clean Energy',
      trl: 7,
      stage: 'Commercial',
      score: 84.2,
      density: 'High',
      innovators: ['QuantumScape', 'Solid Power', 'Toyota', 'Samsung SDI'],
      patents: 1850,
      funding: '$3,200,000,000'
    }
  ];

  const trlDefinitions = [
    { level: 1, name: 'Basic Principles' },
    { level: 2, name: 'Technology Concept' },
    { level: 3, name: 'Experimental Proof' },
    { level: 4, name: 'Lab Validation' },
    { level: 5, name: 'Relevant Environment' },
    { level: 6, name: 'Prototype Demo (Pilot)' },
    { level: 7, name: 'System Prototype' },
    { level: 8, name: 'Qualified System' },
    { level: 9, name: 'Mission Proven' }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-extrabold text-slate-100 tracking-tight flex items-center space-x-2">
          <Cpu className="w-6 h-6 text-cyan-400" />
          <span>Technology Intelligence & TRL Maturity Matrix</span>
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Technology Readiness Level (TRL 1–9) tracking, adoption S-curve modeling, and competitive innovator monitoring.
        </p>
      </div>

      {/* TRL Pipeline Matrix Visualizer */}
      <div className="p-5 rounded-2xl glass-panel space-y-4">
        <h3 className="text-sm font-bold text-slate-200 flex items-center space-x-2">
          <Activity className="w-4 h-4 text-cyan-400" />
          <span>TRL 1–9 Maturity Pipeline Matrix</span>
        </h3>

        <div className="grid grid-cols-9 gap-1.5 pt-2">
          {trlDefinitions.map(t => (
            <div key={t.level} className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-center space-y-1">
              <div className="text-xs font-black text-cyan-400">TRL {t.level}</div>
              <div className="text-[9px] text-slate-400 line-clamp-2 leading-tight">{t.name}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Technology List */}
      <div className="space-y-4">
        <h3 className="text-sm font-bold text-slate-200">Monitored Emerging Technologies</h3>

        <div className="space-y-3">
          {technologies.map(t => (
            <div key={t.name} className="p-5 rounded-2xl glass-panel glass-panel-hover border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="space-y-2 flex-1">
                <div className="flex items-center space-x-3">
                  <span className="px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 text-[10px] font-bold border border-cyan-500/30">{t.domain}</span>
                  <span className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 text-[10px] font-bold border border-amber-500/30">TRL {t.trl} ({t.stage})</span>
                </div>

                <h4 className="text-base font-bold text-slate-100">{t.name}</h4>
                
                <div className="text-xs text-slate-400">
                  Key Innovators: <span className="text-slate-200 font-medium">{t.innovators.join(', ')}</span>
                </div>
              </div>

              <div className="flex items-center space-x-6 bg-slate-900/90 p-4 rounded-xl border border-slate-800 text-right">
                <div>
                  <div className="text-[10px] text-slate-400 uppercase font-semibold">Market Readiness</div>
                  <div className="text-lg font-bold text-emerald-400">{t.score}/100</div>
                </div>
                <div>
                  <div className="text-[10px] text-slate-400 uppercase font-semibold">Funding Volume</div>
                  <div className="text-sm font-bold text-slate-100">{t.funding}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
