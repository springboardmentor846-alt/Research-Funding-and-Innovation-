import React, { useState } from 'react';
import { Award, Sparkles, Sliders, CheckCircle2, Rocket, Building, ShieldCheck, FileText, ArrowRight } from 'lucide-react';

export const InnovationScorer = () => {
  const [projectTitle, setProjectTitle] = useState('Neuromorphic Edge AI Processor for Autonomous Drones');
  const [domain, setDomain] = useState('Artificial Intelligence');
  const [description, setDescription] = useState('Developing ultra-low power spiking neural network chip capable of onboard flight obstacle avoidance at sub-watt power budgets.');

  // Sub-scores (0 - 100)
  const [novelty, setNovelty] = useState(92);
  const [patentStrength, setPatentStrength] = useState(85);
  const [techMaturity, setTechMaturity] = useState(70);
  const [marketPotential, setMarketPotential] = useState(88);
  const [fundingRelevance, setFundingRelevance] = useState(90);

  // Exact PDF Weighted Score Formula
  const calculatedTotalScore = Number(
    ((novelty * 0.30) + (patentStrength * 0.20) + (techMaturity * 0.15) + (marketPotential * 0.20) + (fundingRelevance * 0.15)).toFixed(1)
  );

  const [evaluationResult, setEvaluationResult] = useState(null);

  const handleEvaluate = (e) => {
    e.preventDefault();

    // Generate commercialization recommendations based on scores
    const productization = techMaturity >= 70 ? [
      `Prepare direct MVP commercial roll-out in ${domain}.`,
      "Initiate pilot customer deployments with corporate drone and edge AI partners.",
      "Establish ISO quality assurance and compliance certification frameworks."
    ] : [
      `Conduct proof-of-concept testing in lab environment for ${domain}.`,
      "Focus on prototype validation and functional prototype testing (TRL 4-6)."
    ];

    const licensing = marketPotential >= 75 ? [
      `Execute non-exclusive licensing agreements with tier-1 enterprise leaders in ${domain}.`,
      "Structure milestone-based royalty model (3-7% net sales revenue).",
      "File international PCT patent applications to safeguard licensing territory."
    ] : [
      "Establish field-of-use restrictive licensing with targeted niche vendors."
    ];

    const startup = calculatedTotalScore >= 75 ? [
      "Incorporate a university spin-out or deep-tech startup entity.",
      "Target Y Combinator, NSF I-Corps, or specialized deep-tech accelerators.",
      "Recruit commercial co-founder with go-to-market execution track record."
    ] : [
      "Participate in incubator pre-seed ideation cohorts."
    ];

    const partnerships = [
      `Form joint development agreement (JDA) with established R&D centers in ${domain}.`,
      "Co-publish industry whitepapers to build market domain authority."
    ];

    setEvaluationResult({
      totalScore: calculatedTotalScore,
      productization,
      licensing,
      startup,
      partnerships
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-extrabold text-slate-100 tracking-tight flex items-center space-x-2">
          <Award className="w-6 h-6 text-amber-400" />
          <span>Innovation Scoring Engine & Commercialization Advisory</span>
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Weighted Scoring Model: <span className="text-cyan-400 font-semibold">Innovation Score = Novelty (30%) + Patent Strength (20%) + Tech Maturity (15%) + Market Potential (20%) + Funding Relevance (15%)</span>
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Form Inputs & Sliders */}
        <div className="lg:col-span-7 p-6 rounded-2xl glass-panel space-y-5 border border-slate-800">
          <h3 className="text-base font-bold text-slate-200 flex items-center space-x-2">
            <Sliders className="w-4 h-4 text-cyan-400" />
            <span>Project Parameters & Factor Sliders</span>
          </h3>

          <form onSubmit={handleEvaluate} className="space-y-4">
            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1">Project / Proposal Title</label>
              <input
                type="text"
                value={projectTitle}
                onChange={(e) => setProjectTitle(e.target.value)}
                className="w-full bg-slate-900 text-xs text-slate-200 p-2.5 rounded-lg border border-slate-800 focus:outline-none focus:border-cyan-500"
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Innovation Domain</label>
                <select
                  value={domain}
                  onChange={(e) => setDomain(e.target.value)}
                  className="w-full bg-slate-900 text-xs text-slate-200 p-2.5 rounded-lg border border-slate-800 focus:outline-none focus:border-cyan-500"
                >
                  <option value="Artificial Intelligence">Artificial Intelligence</option>
                  <option value="Quantum Computing">Quantum Computing</option>
                  <option value="Clean Energy">Clean Energy</option>
                  <option value="Biotechnology">Biotechnology</option>
                  <option value="Robotics">Robotics</option>
                </select>
              </div>
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Calculated Total Score</label>
                <div className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-center font-black text-lg text-amber-400">
                  {calculatedTotalScore} / 100
                </div>
              </div>
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1">Executive Summary / Abstract</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={2}
                className="w-full bg-slate-900 text-xs text-slate-200 p-2.5 rounded-lg border border-slate-800 focus:outline-none focus:border-cyan-500"
              />
            </div>

            {/* Sliders */}
            <div className="space-y-3 pt-2 border-t border-slate-800/80">
              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="font-semibold text-slate-300">1. Research Novelty (30% Weight)</span>
                  <span className="text-cyan-400 font-bold">{novelty} / 100</span>
                </div>
                <input
                  type="range" min="0" max="100" value={novelty} onChange={(e) => setNovelty(Number(e.target.value))}
                  className="w-full accent-cyan-500"
                />
              </div>

              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="font-semibold text-slate-300">2. Patent Strength (20% Weight)</span>
                  <span className="text-purple-400 font-bold">{patentStrength} / 100</span>
                </div>
                <input
                  type="range" min="0" max="100" value={patentStrength} onChange={(e) => setPatentStrength(Number(e.target.value))}
                  className="w-full accent-purple-500"
                />
              </div>

              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="font-semibold text-slate-300">3. Technology Maturity (15% Weight)</span>
                  <span className="text-amber-400 font-bold">{techMaturity} / 100</span>
                </div>
                <input
                  type="range" min="0" max="100" value={techMaturity} onChange={(e) => setTechMaturity(Number(e.target.value))}
                  className="w-full accent-amber-500"
                />
              </div>

              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="font-semibold text-slate-300">4. Market Potential (20% Weight)</span>
                  <span className="text-emerald-400 font-bold">{marketPotential} / 100</span>
                </div>
                <input
                  type="range" min="0" max="100" value={marketPotential} onChange={(e) => setMarketPotential(Number(e.target.value))}
                  className="w-full accent-emerald-500"
                />
              </div>

              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="font-semibold text-slate-300">5. Funding Relevance (15% Weight)</span>
                  <span className="text-blue-400 font-bold">{fundingRelevance} / 100</span>
                </div>
                <input
                  type="range" min="0" max="100" value={fundingRelevance} onChange={(e) => setFundingRelevance(Number(e.target.value))}
                  className="w-full accent-blue-500"
                />
              </div>
            </div>

            <button
              type="submit"
              className="w-full py-3 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-black text-xs uppercase tracking-wider transition-all shadow-lg shadow-amber-500/20"
            >
              Run AI Commercialization Advisory Engine
            </button>
          </form>
        </div>

        {/* Results Panel */}
        <div className="lg:col-span-5 space-y-4">
          <div className="p-6 rounded-2xl glass-panel border border-slate-800 space-y-4 text-center">
            <div className="text-xs text-slate-400 uppercase font-semibold">Calculated Composite Innovation Score</div>
            <div className="w-24 h-24 rounded-full bg-gradient-to-tr from-amber-500 via-amber-400 to-yellow-300 mx-auto flex items-center justify-center text-slate-950 text-3xl font-black shadow-xl shadow-amber-500/30">
              {calculatedTotalScore}
            </div>
            <div className="text-xs text-emerald-400 font-semibold">
              {calculatedTotalScore >= 80 ? 'Grade A+: High Commercialization Potential' : 'Grade B: Moderate Commercial Readiness'}
            </div>
          </div>

          {evaluationResult && (
            <div className="p-5 rounded-2xl glass-panel border border-slate-800 space-y-4 animate-in fade-in">
              <h4 className="text-xs font-bold uppercase text-slate-400 tracking-wider flex items-center space-x-2">
                <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                <span>AI Commercialization Recommendations</span>
              </h4>

              <div className="space-y-3 text-xs">
                <div className="space-y-1">
                  <div className="font-semibold text-cyan-300 flex items-center space-x-1.5">
                    <Rocket className="w-3.5 h-3.5" />
                    <span>Productization Strategy</span>
                  </div>
                  <ul className="list-disc pl-4 text-slate-400 space-y-0.5">
                    {evaluationResult.productization.map((item, i) => <li key={i}>{item}</li>)}
                  </ul>
                </div>

                <div className="space-y-1">
                  <div className="font-semibold text-purple-300 flex items-center space-x-1.5">
                    <ShieldCheck className="w-3.5 h-3.5" />
                    <span>Licensing & IP Advisory</span>
                  </div>
                  <ul className="list-disc pl-4 text-slate-400 space-y-0.5">
                    {evaluationResult.licensing.map((item, i) => <li key={i}>{item}</li>)}
                  </ul>
                </div>

                <div className="space-y-1">
                  <div className="font-semibold text-emerald-300 flex items-center space-x-1.5">
                    <Building className="w-3.5 h-3.5" />
                    <span>Startup Creation Roadmap</span>
                  </div>
                  <ul className="list-disc pl-4 text-slate-400 space-y-0.5">
                    {evaluationResult.startup.map((item, i) => <li key={i}>{item}</li>)}
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
