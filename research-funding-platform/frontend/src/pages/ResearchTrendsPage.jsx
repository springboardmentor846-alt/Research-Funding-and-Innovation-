import React, { useState, useEffect } from 'react';
import { Navbar } from '../components/common/Navbar';
import { Sidebar } from '../components/common/Sidebar';
import { Footer } from '../components/common/Footer';
import { intelligenceAPI } from '../services/api';
import { Loader } from '../components/common/Loader';
import { BookOpen, Sparkles, Award, TrendingUp, Search, ExternalLink } from 'lucide-react';

export const ResearchTrendsPage = () => {
  const [pubs, setPubs] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  const [aiPaper, setAiPaper] = useState({ title: '', abstract: '' });
  const [aiResult, setAiResult] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);

  useEffect(() => {
    Promise.all([
      intelligenceAPI.getPublications(),
      intelligenceAPI.getResearchAnalytics()
    ]).then(([pRes, aRes]) => {
      setPubs(pRes.data);
      setAnalytics(aRes.data);
    }).catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const handleAnalyze = async (e) => {
    e.preventDefault();
    setAnalyzing(true);
    try {
      const res = await intelligenceAPI.analyzePaper(aiPaper);
      setAiResult(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setAnalyzing(false);
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
              Research Trends & Citation Intelligence
            </h1>
            <p className="text-sm text-slate-400 mt-1">Track high-impact publications, topic clusters, and citation velocity.</p>
          </div>

          {loading ? (
            <Loader message="Gathering publication & citation intelligence..." />
          ) : (
            <>
              {/* Analytics Header Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="glass-card p-6 flex items-center space-x-4">
                  <div className="p-3 bg-blue-500/20 text-blue-400 rounded-xl">
                    <BookOpen className="w-6 h-6" />
                  </div>
                  <div>
                    <div className="text-xs text-slate-400 font-semibold uppercase">Tracked Papers</div>
                    <div className="text-2xl font-bold">{analytics?.total_publications}</div>
                  </div>
                </div>

                <div className="glass-card p-6 flex items-center space-x-4">
                  <div className="p-3 bg-teal-500/20 text-teal-400 rounded-xl">
                    <TrendingUp className="w-6 h-6" />
                  </div>
                  <div>
                    <div className="text-xs text-slate-400 font-semibold uppercase">Total Citations</div>
                    <div className="text-2xl font-bold">{analytics?.total_citations}</div>
                  </div>
                </div>

                <div className="glass-card p-6 flex items-center space-x-4">
                  <div className="p-3 bg-purple-500/20 text-purple-400 rounded-xl">
                    <Award className="w-6 h-6" />
                  </div>
                  <div>
                    <div className="text-xs text-slate-400 font-semibold uppercase">Avg Impact Factor</div>
                    <div className="text-2xl font-bold">{analytics?.average_impact_factor}</div>
                  </div>
                </div>
              </div>

              {/* AI Paper Abstract Analyzer Tool */}
              <div className="glass-card p-6 space-y-4">
                <div className="flex items-center space-x-2">
                  <Sparkles className="w-5 h-5 text-blue-400" />
                  <h3 className="text-lg font-bold">AI Paper Novelty & Key Findings Extractor</h3>
                </div>

                <form onSubmit={handleAnalyze} className="space-y-3">
                  <input
                    type="text"
                    required
                    placeholder="Paper Title..."
                    value={aiPaper.title}
                    onChange={(e) => setAiPaper({...aiPaper, title: e.target.value})}
                    className="w-full p-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm"
                  />
                  <textarea
                    rows={3}
                    required
                    placeholder="Paste publication abstract here to extract key novelty..."
                    value={aiPaper.abstract}
                    onChange={(e) => setAiPaper({...aiPaper, abstract: e.target.value})}
                    className="w-full p-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm"
                  />
                  <button
                    type="submit"
                    disabled={analyzing}
                    className="px-6 py-2.5 rounded-xl font-bold text-white gradient-bg-accent shadow-md text-sm"
                  >
                    {analyzing ? 'Analyzing Abstract...' : 'Run AI Analysis'}
                  </button>
                </form>

                {aiResult && (
                  <div className="p-4 bg-slate-950/80 border border-blue-500/30 rounded-xl space-y-2 text-sm">
                    <div className="font-bold text-blue-400">{aiResult.ai_summary}</div>
                    <div className="text-xs text-slate-400">Confidence: {(aiResult.confidence_score * 100).toFixed(0)}% • Engine: {aiResult.model_used}</div>
                    <div className="flex space-x-2 pt-1">
                      {aiResult.suggested_tags?.map((t, idx) => (
                        <span key={idx} className="px-2 py-0.5 bg-slate-800 text-slate-300 text-xs rounded-md">{t}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Publications List */}
              <div className="space-y-4">
                <h3 className="text-xl font-bold">Recent Scientific Publications</h3>
                <div className="space-y-4">
                  {pubs.map((p) => (
                    <div key={p.id} className="glass-card p-6 space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-semibold text-teal-400">{p.journal} • IF {p.impact_factor}</span>
                        <span className="text-xs text-slate-400 font-medium">{p.citations_count} Citations</span>
                      </div>
                      <h4 className="text-lg font-bold text-slate-100">{p.title}</h4>
                      <div className="text-xs text-slate-400 font-medium">Authors: {p.authors} ({p.publication_date})</div>
                      <p className="text-sm text-slate-300">{p.abstract}</p>
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
