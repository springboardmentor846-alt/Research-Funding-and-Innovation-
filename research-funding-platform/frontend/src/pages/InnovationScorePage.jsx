import React, { useState, useEffect } from 'react';
import { Navbar } from '../components/common/Navbar';
import { Sidebar } from '../components/common/Sidebar';
import { Footer } from '../components/common/Footer';
import { scoringAPI } from '../services/api';
import { Loader } from '../components/common/Loader';
import { Gauge, Calculator, CheckCircle2, Award, Sparkles } from 'lucide-react';

export const InnovationScorePage = () => {
  const [scores, setScores] = useState([]);
  const [loading, setLoading] = useState(true);
  const [calculating, setCalculating] = useState(false);

  const entityDefaults = {
    Research: {
      entity_name: 'Quantum AI Diagnostic System',
      novelty_score: 92,
      patent_strength: 60,
      tech_maturity: 45,
      market_potential: 80,
      funding_relevance: 95
    },
    Startup: {
      entity_name: 'Solaria Battery Storage Inc',
      novelty_score: 75,
      patent_strength: 80,
      tech_maturity: 85,
      market_potential: 95,
      funding_relevance: 70
    },
    Patent: {
      entity_name: 'Josephson Qubit Resonator Portfolio',
      novelty_score: 88,
      patent_strength: 95,
      tech_maturity: 65,
      market_potential: 70,
      funding_relevance: 60
    },
    Technology: {
      entity_name: 'Decarbonized Hydrogen Electrolyzer',
      novelty_score: 65,
      patent_strength: 75,
      tech_maturity: 90,
      market_potential: 85,
      funding_relevance: 80
    }
  };

  const [formData, setFormData] = useState({
    entity_type: 'Research',
    entity_name: 'Quantum AI Diagnostic System',
    novelty_score: 92,
    patent_strength: 60,
    tech_maturity: 45,
    market_potential: 80,
    funding_relevance: 95
  });

  const [activeScore, setActiveScore] = useState(null);

  const handleEntityTypeChange = (type) => {
    const defaults = entityDefaults[type];
    setFormData({
      entity_type: type,
      ...defaults
    });
  };

  const fetchScores = async () => {
    try {
      const res = await scoringAPI.getScores();
      setScores(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchScores();
  }, []);

  const handleCalculate = async (e) => {
    e.preventDefault();
    setCalculating(true);
    try {
      const res = await scoringAPI.calculateScore(formData);
      setActiveScore(res.data);
      fetchScores();
    } catch (e) {
      console.error(e);
    } finally {
      setCalculating(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
      <Navbar />
      <div className="flex-1 flex">
        <Sidebar />
        <main className="flex-1 p-8 space-y-8 overflow-y-auto">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight gradient-text flex items-center space-x-2">
              <Gauge className="w-8 h-8 text-amber-400" />
              <span>Multi-Factor Innovation Scoring Engine</span>
            </h1>
            <p className="text-sm text-slate-400 mt-1">Quantitative evaluation combining research novelty, IP strength, TRL maturity, market potential, and grant alignment.</p>
          </div>

          {/* Calculator Section */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <form onSubmit={handleCalculate} className="glass-card p-6 space-y-4">
              <div className="flex items-center space-x-2 border-b border-slate-800 pb-3">
                <Calculator className="w-5 h-5 text-blue-400" />
                <h3 className="text-lg font-bold">Interactive Score Calculator</h3>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Entity Type</label>
                  <select
                    value={formData.entity_type}
                    onChange={(e) => handleEntityTypeChange(e.target.value)}
                    className="w-full p-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm"
                  >
                    <option value="Research">Research Proposal</option>
                    <option value="Startup">Startup Spin-off</option>
                    <option value="Patent">Patent Portfolio</option>
                    <option value="Technology">Technology Asset</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Entity Name</label>
                  <input
                    type="text"
                    required
                    value={formData.entity_name}
                    onChange={(e) => setFormData({...formData, entity_name: e.target.value})}
                    className="w-full p-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm"
                  />
                </div>
              </div>

              {/* Sliders */}
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between text-xs font-semibold mb-1">
                    <span>Research Novelty (25% Weight)</span>
                    <span className="text-blue-400">{formData.novelty_score}/100</span>
                  </div>
                  <input type="range" min="0" max="100" value={formData.novelty_score} onChange={(e) => setFormData({...formData, novelty_score: parseFloat(e.target.value)})} className="w-full accent-blue-500" />
                </div>

                <div>
                  <div className="flex justify-between text-xs font-semibold mb-1">
                    <span>Patent Strength (20% Weight)</span>
                    <span className="text-teal-400">{formData.patent_strength}/100</span>
                  </div>
                  <input type="range" min="0" max="100" value={formData.patent_strength} onChange={(e) => setFormData({...formData, patent_strength: parseFloat(e.target.value)})} className="w-full accent-teal-500" />
                </div>

                <div>
                  <div className="flex justify-between text-xs font-semibold mb-1">
                    <span>Tech Maturity (20% Weight)</span>
                    <span className="text-purple-400">{formData.tech_maturity}/100</span>
                  </div>
                  <input type="range" min="0" max="100" value={formData.tech_maturity} onChange={(e) => setFormData({...formData, tech_maturity: parseFloat(e.target.value)})} className="w-full accent-purple-500" />
                </div>

                <div>
                  <div className="flex justify-between text-xs font-semibold mb-1">
                    <span>Market Potential (20% Weight)</span>
                    <span className="text-amber-400">{formData.market_potential}/100</span>
                  </div>
                  <input type="range" min="0" max="100" value={formData.market_potential} onChange={(e) => setFormData({...formData, market_potential: parseFloat(e.target.value)})} className="w-full accent-amber-500" />
                </div>

                <div>
                  <div className="flex justify-between text-xs font-semibold mb-1">
                    <span>Funding Relevance (15% Weight)</span>
                    <span className="text-emerald-400">{formData.funding_relevance}/100</span>
                  </div>
                  <input type="range" min="0" max="100" value={formData.funding_relevance} onChange={(e) => setFormData({...formData, funding_relevance: parseFloat(e.target.value)})} className="w-full accent-emerald-500" />
                </div>
              </div>

              <button type="submit" disabled={calculating} className="w-full py-3 rounded-xl font-bold text-white gradient-bg-accent shadow-lg">
                {calculating ? 'Computing Algorithm...' : 'Calculate Innovation Score'}
              </button>
            </form>

            {/* Score Result Gauge */}
            <div className="glass-card p-6 flex flex-col justify-between space-y-4">
              <h3 className="text-lg font-bold border-b border-slate-800 pb-3">Automated Evaluation Output</h3>

              {activeScore ? (
                <div className="space-y-6 text-center">
                  <div className="inline-flex flex-col items-center justify-center w-36 h-36 rounded-full bg-slate-950 border-4 border-emerald-500 shadow-2xl mx-auto">
                    <span className="text-4xl font-extrabold text-emerald-400">{activeScore.overall_score}</span>
                    <span className="text-xs text-slate-400 uppercase font-semibold">Score / 100</span>
                  </div>

                  <div className="p-4 bg-slate-950/80 border border-slate-800 rounded-xl text-left space-y-2">
                    <div className="text-xs font-bold text-slate-400 uppercase">Commercialization Recommendations</div>
                    <p className="text-sm text-slate-200 leading-relaxed">{activeScore.recommendations}</p>
                  </div>
                </div>
              ) : (
                <div className="text-center py-16 text-slate-400 text-sm space-y-2">
                  <Sparkles className="w-10 h-10 mx-auto text-slate-600" />
                  <div>Adjust sliders and click "Calculate Innovation Score" to generate evaluation telemetry.</div>
                </div>
              )}
            </div>
          </div>
        </main>
      </div>
      <Footer />
    </div>
  );
};
