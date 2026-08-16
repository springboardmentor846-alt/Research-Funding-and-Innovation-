import React, { useEffect, useState } from 'react';
import { Navbar } from '../components/common/Navbar';
import { Sidebar } from '../components/common/Sidebar';
import { Footer } from '../components/common/Footer';
import { dashboardAPI, userAPI } from '../services/api';
import { Loader } from '../components/common/Loader';
import { DollarSign, BookOpen, FileCheck, Cpu, Gauge, ArrowUpRight, TrendingUp } from 'lucide-react';
import { Link } from 'react-router-dom';

export const DashboardPage = () => {
  const [overview, setOverview] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      dashboardAPI.getOverview(),
      userAPI.getProfile()
    ]).then(([oRes, pRes]) => {
      setOverview(oRes.data);
      setProfile(pRes.data);
    }).catch(err => console.error(err))
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
              Platform Intelligence Overview
            </h1>
            <p className="text-sm text-slate-400 mt-1">Real-time telemetry across grants, research publications, patent filings, and technology readiness.</p>
          </div>

          {loading ? (
            <Loader message="Synthesizing platform analytics..." />
          ) : (
            <>
              {/* Research Profile Summary Card */}
              {profile && (
                <div className="glass-card p-6 bg-gradient-to-r from-blue-900/10 via-slate-900/40 to-purple-900/10 border border-blue-500/20 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="space-y-1">
                    <div className="text-xs text-blue-400 font-bold uppercase tracking-wider">Active Research Profile</div>
                    <h2 className="text-xl font-bold text-slate-100">{profile.organization || 'MIT AI Lab'}</h2>
                    <div className="text-sm text-slate-300">
                      <span className="font-semibold text-slate-400">Domains:</span> {profile.domains}
                    </div>
                    <div className="text-sm text-slate-300">
                      <span className="font-semibold text-slate-400">Keywords:</span> {profile.keywords}
                    </div>
                  </div>
                  <div className="flex items-center space-x-6 pl-0 md:pl-6 border-t md:border-t-0 md:border-l border-slate-800/80 pt-4 md:pt-0">
                    <div className="text-center">
                      <div className="text-2xl font-black text-blue-400">{profile.publications_count}</div>
                      <div className="text-xs text-slate-400">Publications</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-black text-purple-400">{profile.patents_count}</div>
                      <div className="text-xs text-slate-400">Patents</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-black text-teal-400">{profile.h_index}</div>
                      <div className="text-xs text-slate-400">H-Index</div>
                    </div>
                  </div>
                </div>
              )}

              {/* KPI Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="glass-card p-6 flex items-center space-x-4 border-l-4 border-l-blue-500">
                  <div className="p-3 bg-blue-500/20 rounded-xl text-blue-400">
                    <DollarSign className="w-6 h-6" />
                  </div>
                  <div>
                    <div className="text-xs text-slate-400 uppercase font-semibold">Active Capital Pool</div>
                    <div className="text-2xl font-bold text-slate-100">{overview?.kpis?.total_funding_usd || '$13.0M'}</div>
                    <div className="text-xs text-emerald-400 flex items-center mt-0.5">
                      <TrendingUp className="w-3 h-3 mr-1" /> {overview?.kpis?.total_funding_grants || 5} Grants Available
                    </div>
                  </div>
                </div>

                <div className="glass-card p-6 flex items-center space-x-4 border-l-4 border-l-teal-500">
                  <div className="p-3 bg-teal-500/20 rounded-xl text-teal-400">
                    <BookOpen className="w-6 h-6" />
                  </div>
                  <div>
                    <div className="text-xs text-slate-400 uppercase font-semibold">Research Papers</div>
                    <div className="text-2xl font-bold text-slate-100">{overview?.kpis?.total_publications || 3}</div>
                    <div className="text-xs text-slate-400 mt-0.5">High-Impact Journals</div>
                  </div>
                </div>

                <div className="glass-card p-6 flex items-center space-x-4 border-l-4 border-l-purple-500">
                  <div className="p-3 bg-purple-500/20 rounded-xl text-purple-400">
                    <FileCheck className="w-6 h-6" />
                  </div>
                  <div>
                    <div className="text-xs text-slate-400 uppercase font-semibold">Patent Filings</div>
                    <div className="text-2xl font-bold text-slate-100">{overview?.kpis?.total_patents || 3}</div>
                    <div className="text-xs text-purple-400 mt-0.5">Active IP Claims</div>
                  </div>
                </div>

                <div className="glass-card p-6 flex items-center space-x-4 border-l-4 border-l-amber-500">
                  <div className="p-3 bg-amber-500/20 rounded-xl text-amber-400">
                    <Gauge className="w-6 h-6" />
                  </div>
                  <div>
                    <div className="text-xs text-slate-400 uppercase font-semibold">Avg Innovation Score</div>
                    <div className="text-2xl font-bold text-slate-100">{overview?.kpis?.average_innovation_score || 87.6} / 100</div>
                    <div className="text-xs text-amber-400 mt-0.5">Multi-Factor Score</div>
                  </div>
                </div>
              </div>

              {/* Analytics Sections */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Recent Innovation Scores */}
                <div className="glass-card p-6 space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-bold text-slate-100">Top Rated Innovation Entities</h3>
                    <Link to="/innovation-score" className="text-xs text-blue-400 hover:underline flex items-center">
                      View Engine <ArrowUpRight className="w-3 h-3 ml-1" />
                    </Link>
                  </div>
                  <div className="space-y-3">
                    {overview?.recent_innovation_scores?.map((item, idx) => (
                      <div key={idx} className="p-3 bg-slate-950/60 border border-slate-800 rounded-xl flex items-center justify-between">
                        <div>
                          <div className="text-sm font-semibold text-slate-200">{item.name}</div>
                          <div className="text-xs text-slate-400">{item.type} • Novelty {item.novelty}%</div>
                        </div>
                        <div className="px-3 py-1 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 rounded-lg font-bold text-sm">
                          {item.score} / 100
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Quick Action Matrix */}
                <div className="glass-card p-6 space-y-4">
                  <h3 className="text-lg font-bold text-slate-100">Quick Intelligence Actions</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <Link to="/recommendations" className="p-4 bg-slate-950/60 hover:bg-slate-900 border border-slate-800 rounded-xl transition-all block">
                      <div className="font-semibold text-sm text-blue-400">Match Grants AI</div>
                      <div className="text-xs text-slate-400 mt-1">Run eligibility similarity matcher on profile.</div>
                    </Link>
                    <Link to="/innovation-score" className="p-4 bg-slate-950/60 hover:bg-slate-900 border border-slate-800 rounded-xl transition-all block">
                      <div className="font-semibold text-sm text-teal-400">Compute Score</div>
                      <div className="text-xs text-slate-400 mt-1">Calculate multi-factor novelty & market score.</div>
                    </Link>
                    <Link to="/patent-analytics" className="p-4 bg-slate-950/60 hover:bg-slate-900 border border-slate-800 rounded-xl transition-all block">
                      <div className="font-semibold text-sm text-purple-400">Patent Search</div>
                      <div className="text-xs text-slate-400 mt-1">Explore assignees, claims, and filing status.</div>
                    </Link>
                    <Link to="/reports" className="p-4 bg-slate-950/60 hover:bg-slate-900 border border-slate-800 rounded-xl transition-all block">
                      <div className="font-semibold text-sm text-amber-400">Export Reports</div>
                      <div className="text-xs text-slate-400 mt-1">Generate verified CSV & PDF digests.</div>
                    </Link>
                  </div>
                </div>
              </div>
            </>
          )}
        </main>
      </div>
      <Footer />
    </div>
  );
};
