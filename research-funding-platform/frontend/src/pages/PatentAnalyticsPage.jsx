import React, { useState, useEffect } from 'react';
import { Navbar } from '../components/common/Navbar';
import { Sidebar } from '../components/common/Sidebar';
import { Footer } from '../components/common/Footer';
import { intelligenceAPI } from '../services/api';
import { Loader } from '../components/common/Loader';
import { FileCheck, Shield, Building, Filter, Search } from 'lucide-react';

export const PatentAnalyticsPage = () => {
  const [patents, setPatents] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [techField, setTechField] = useState('All');
  const [query, setQuery] = useState('');

  useEffect(() => {
    Promise.all([
      intelligenceAPI.getPatents({ query, tech_field: techField }),
      intelligenceAPI.getPatentAnalytics()
    ]).then(([pRes, aRes]) => {
      setPatents(pRes.data);
      setAnalytics(aRes.data);
    }).catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, [techField]);

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
      <Navbar />
      <div className="flex-1 flex">
        <Sidebar />
        <main className="flex-1 p-8 space-y-8 overflow-y-auto">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight gradient-text">
              Patent Landscape & IP Intelligence
            </h1>
            <p className="text-sm text-slate-400 mt-1">Explore assignee clusters, claim counts, prior-art overlaps, and filing statuses.</p>
          </div>

          {loading ? (
            <Loader message="Mining patent landscape database..." />
          ) : (
            <>
              {/* Analytics Top Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="glass-card p-6 flex items-center space-x-4">
                  <div className="p-3 bg-purple-500/20 text-purple-400 rounded-xl">
                    <FileCheck className="w-6 h-6" />
                  </div>
                  <div>
                    <div className="text-xs text-slate-400 font-semibold uppercase">Total Patents Tracked</div>
                    <div className="text-2xl font-bold">{analytics?.total_patents}</div>
                  </div>
                </div>

                <div className="glass-card p-6 flex items-center space-x-4">
                  <div className="p-3 bg-emerald-500/20 text-emerald-400 rounded-xl">
                    <Shield className="w-6 h-6" />
                  </div>
                  <div>
                    <div className="text-xs text-slate-400 font-semibold uppercase">Active Granted Claims</div>
                    <div className="text-2xl font-bold text-emerald-400">{analytics?.active_patents}</div>
                  </div>
                </div>

                <div className="glass-card p-6 flex items-center space-x-4">
                  <div className="p-3 bg-amber-500/20 text-amber-400 rounded-xl">
                    <Building className="w-6 h-6" />
                  </div>
                  <div>
                    <div className="text-xs text-slate-400 font-semibold uppercase">Top Assignees</div>
                    <div className="text-sm font-semibold text-slate-200 truncate mt-1">
                      {analytics?.top_assignees?.map(a => a.assignee).join(', ')}
                    </div>
                  </div>
                </div>
              </div>

              {/* Patent Grid */}
              <div className="space-y-4">
                <h3 className="text-xl font-bold">Patent Portfolio Entries</h3>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {patents.map((p) => (
                    <div key={p.id} className="glass-card p-6 space-y-3 flex flex-col justify-between">
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="px-3 py-1 bg-purple-500/10 border border-purple-500/30 text-purple-400 text-xs font-bold rounded-lg">
                            {p.patent_number}
                          </span>
                          <span className={`text-xs font-bold px-2 py-0.5 rounded-md ${
                            p.status === 'Active' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-amber-500/10 text-amber-400'
                          }`}>
                            {p.status}
                          </span>
                        </div>
                        <h4 className="text-lg font-bold text-slate-100">{p.title}</h4>
                        <div className="text-xs text-slate-400">Assignee: <strong className="text-slate-200">{p.assignee}</strong> • Field: {p.tech_field}</div>
                        <p className="text-sm text-slate-300">{p.abstract}</p>
                      </div>

                      <div className="pt-3 border-t border-slate-800 text-xs text-slate-400 flex items-center justify-between">
                        <span>Claims Count: <strong>{p.claims_count}</strong></span>
                        <span>Filed: {p.filing_date}</span>
                      </div>
                    </div>
                  ))}
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
