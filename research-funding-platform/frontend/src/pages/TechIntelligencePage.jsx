import React, { useState, useEffect } from 'react';
import { Navbar } from '../components/common/Navbar';
import { Sidebar } from '../components/common/Sidebar';
import { Footer } from '../components/common/Footer';
import { intelligenceAPI } from '../services/api';
import { Loader } from '../components/common/Loader';
import { Cpu, TrendingUp, Gauge, DollarSign } from 'lucide-react';

export const TechIntelligencePage = () => {
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    intelligenceAPI.getTechTrends()
      .then(res => setTrends(res.data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
      <Navbar />
      <div className="flex-1 flex">
        <Sidebar />
        <main className="flex-1 p-8 space-y-8 overflow-y-auto">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight gradient-text">
              Technology Intelligence & Readiness Radar
            </h1>
            <p className="text-sm text-slate-400 mt-1">Monitor emerging technology trajectories, Technology Readiness Levels (TRL 1-9), and market potential.</p>
          </div>

          {loading ? (
            <Loader message="Scanning global tech readiness database..." />
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {trends.map((t) => (
                <div key={t.id} className="glass-card p-6 space-y-4 flex flex-col justify-between">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="px-3 py-1 bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-bold rounded-lg">
                        TRL Level {t.readiness_level} / 9
                      </span>
                      <span className="text-xs font-bold text-emerald-400 flex items-center">
                        <TrendingUp className="w-3.5 h-3.5 mr-1" /> +{t.growth_rate}% YoY
                      </span>
                    </div>

                    <h3 className="text-xl font-bold text-slate-100">{t.technology_name}</h3>
                    <div className="text-xs font-semibold text-blue-400">{t.category} • {t.adoption_stage} Stage</div>
                    <p className="text-sm text-slate-300">{t.description}</p>
                  </div>

                  <div className="pt-3 border-t border-slate-800 flex items-center justify-between text-xs">
                    <span className="text-slate-400">Est. Market Size</span>
                    <span className="font-extrabold text-slate-100 text-sm">{t.market_size_est}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </main>
      </div>
      <Footer />
    </div>
  );
};
