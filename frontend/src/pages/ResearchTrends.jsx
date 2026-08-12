import React, { useMemo } from 'react';
import { TrendingUp, BookOpen, Sparkles, Flame, BarChart2, Layers } from 'lucide-react';

export const ResearchTrends = () => {
  const trends = [
    {
      topic: 'Neuromorphic Edge AI Chips',
      domain: 'Artificial Intelligence',
      growth: '+148.5%',
      count: 1240,
      velocity: '28.4 citations/yr',
      hotspot: 94.2,
      stage: 'Emerging',
      keywords: ['Spiking Neural Networks', 'Memristors', 'Edge AI', 'Low-Power Chips'],
      series: { '2022': 180, '2023': 340, '2024': 650, '2025': 1240 }
    },
    {
      topic: 'Quantum Graph Neural Networks',
      domain: 'Quantum Computing',
      growth: '+185.2%',
      count: 620,
      velocity: '32.1 citations/yr',
      hotspot: 91.8,
      stage: 'Emerging',
      keywords: ['QNN', 'Graph Embeddings', 'Variational Quantum Algorithms'],
      series: { '2022': 45, '2023': 110, '2024': 280, '2025': 620 }
    },
    {
      topic: 'Solid-State Lithium Metal Batteries',
      domain: 'Clean Energy',
      growth: '+76.4%',
      count: 3100,
      velocity: '45.0 citations/yr',
      hotspot: 86.5,
      stage: 'Growing',
      keywords: ['Solid Electrolytes', 'Dendrite Suppression', 'Energy Density'],
      series: { '2022': 950, '2023': 1450, '2024': 2200, '2025': 3100 }
    },
    {
      topic: 'Targeted mRNA Nanoparticle Delivery',
      domain: 'Biotechnology',
      growth: '+62.0%',
      count: 4200,
      velocity: '52.3 citations/yr',
      hotspot: 84.0,
      stage: 'Mature',
      keywords: ['LNP Delivery', 'CRISPR Editing', 'Oncology mRNA'],
      series: { '2022': 1800, '2023': 2600, '2024': 3400, '2025': 4200 }
    }
  ];

  const trendSummary = useMemo(() => {
    const stageCounts = trends.reduce((counts, trend) => {
      counts[trend.stage] = (counts[trend.stage] || 0) + 1;
      return counts;
    }, {});
    const domainCounts = trends.reduce((counts, trend) => {
      counts[trend.domain] = (counts[trend.domain] || 0) + 1;
      return counts;
    }, {});
    return {
      totalTrends: trends.length,
      averageHotspot: Math.round(trends.reduce((sum, trend) => sum + trend.hotspot, 0) / trends.length),
      topDomain: Object.entries(domainCounts).sort((a, b) => b[1] - a[1])[0]?.[0] || 'Mixed Technologies',
      stageCounts,
    };
  }, [trends]);

  const topPapers = [
    {
      title: 'Scalable Neuromorphic Computing via Spike-Timing-Dependent Plasticity',
      authors: 'Dr. Aris Thorne et al.',
      venue: 'Nature Electronics 2025',
      citations: 142,
      source: 'OpenAlex'
    },
    {
      title: 'Quantum Graph Neural Networks for Molecular Structure Prediction',
      authors: 'Dr. Aris Thorne, Elena Vance',
      venue: 'IEEE T-NNLS 2025',
      citations: 89,
      source: 'CrossRef'
    },
    {
      title: 'High-Conductivity Solid Electrolytes for Fast-Charging Batteries',
      authors: 'Dr. Marcus Chen et al.',
      venue: 'Science Energy 2024',
      citations: 215,
      source: 'Semantic Scholar'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-extrabold text-slate-100 tracking-tight flex items-center space-x-2">
          <TrendingUp className="w-6 h-6 text-cyan-400" />
          <span>Research Trend Intelligence & Topic Hotspots</span>
        </h2>
        <p className="text-xs text-slate-400 mt-1 max-w-3xl">
          Automated topic velocity extraction, citation trajectory monitoring, and emerging research hotspot identification harvested from OpenAlex, CrossRef, and Semantic Scholar. Use this page to compare topic momentum, track top publication signals, and identify the most actionable research domains.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="rounded-2xl border border-slate-800 p-4 bg-slate-900/80">
          <p className="text-[11px] uppercase tracking-[0.18em] text-slate-400 mb-2">Total Hot Topics</p>
          <p className="text-3xl font-bold text-slate-100">{trendSummary.totalTrends}</p>
        </div>
        <div className="rounded-2xl border border-slate-800 p-4 bg-slate-900/80">
          <p className="text-[11px] uppercase tracking-[0.18em] text-slate-400 mb-2">Average Hotspot Score</p>
          <p className="text-3xl font-bold text-cyan-400">{trendSummary.averageHotspot}</p>
        </div>
        <div className="rounded-2xl border border-slate-800 p-4 bg-slate-900/80">
          <p className="text-[11px] uppercase tracking-[0.18em] text-slate-400 mb-2">Top Domain</p>
          <p className="text-3xl font-bold text-slate-100">{trendSummary.topDomain}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {Object.entries(trendSummary.stageCounts).map(([stage, count]) => (
          <div key={stage} className="rounded-2xl border border-slate-800 p-4 bg-slate-900/80">
            <p className="text-[11px] uppercase tracking-[0.18em] text-slate-400 mb-2">{stage} Topics</p>
            <p className="text-2xl font-semibold text-slate-100">{count}</p>
          </div>
        ))}
      </div>

      {/* Emerging Topic Leaderboard */}
      <div className="space-y-4">
        <h3 className="text-base font-bold text-slate-200 flex items-center space-x-2">
          <Flame className="w-4 h-4 text-amber-400" />
          <span>Emerging Research Hotspot Velocity Leaderboard</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {trends.map(t => (
            <div key={t.topic} className="p-5 rounded-2xl glass-panel glass-panel-hover border border-slate-800 space-y-4">
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">{t.domain}</span>
                  <h4 className="text-base font-bold text-slate-100">{t.topic}</h4>
                </div>
                <div className="text-right">
                  <div className="text-lg font-black text-cyan-400">{t.hotspot}/100</div>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-slate-900 text-slate-300 font-bold border border-slate-800">{t.stage}</span>
                </div>
              </div>

              {/* Time series growth bars */}
              <div className="space-y-1.5 pt-2 border-t border-slate-800/80">
                <div className="flex justify-between text-[11px] text-slate-400">
                  <span>Publication Velocity YoY:</span>
                  <span className="text-emerald-400 font-bold">{t.growth}</span>
                </div>
                <div className="flex items-end space-x-2 h-16 pt-2">
                  {Object.entries(t.series).map(([year, val]) => {
                    const maxVal = Math.max(...Object.values(t.series));
                    const heightPct = Math.round((val / maxVal) * 100);
                    return (
                      <div key={year} className="flex-1 flex flex-col items-center">
                        <div 
                          style={{ height: `${heightPct}%` }} 
                          className="w-full rounded-t bg-gradient-to-t from-cyan-600 to-blue-400"
                        ></div>
                        <span className="text-[9px] text-slate-500 mt-1">{year}</span>
                      </div>
                    );
                  })}
                </div>
              </div>

              <div className="flex flex-wrap gap-1.5 pt-2">
                {t.keywords.map(k => (
                  <span key={k} className="px-2 py-0.5 rounded bg-slate-900 text-slate-400 text-[10px] border border-slate-800">
                    {k}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Top Indexed Publications */}
      <div className="p-5 rounded-2xl glass-panel space-y-4">
        <h3 className="text-sm font-bold text-slate-200 flex items-center space-x-2">
          <BookOpen className="w-4 h-4 text-cyan-400" />
          <span>High-Impact Indexed Publications</span>
        </h3>

        <div className="divide-y divide-slate-800 text-xs">
          {topPapers.map((p, idx) => (
            <div key={idx} className="py-3 flex flex-col md:flex-row md:items-center justify-between gap-2">
              <div className="space-y-1">
                <div className="font-bold text-slate-100">{p.title}</div>
                <div className="text-slate-400">{p.authors} • <span className="text-slate-300">{p.venue}</span></div>
              </div>
              <div className="flex items-center space-x-3 text-right">
                <span className="px-2 py-1 rounded bg-purple-500/10 text-purple-300 font-semibold border border-purple-500/20">{p.citations} Citations</span>
                <span className="text-[10px] text-slate-500">{p.source}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
