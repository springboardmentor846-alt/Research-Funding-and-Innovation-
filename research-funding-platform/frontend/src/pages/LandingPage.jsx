import React from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, Search, Gauge, Cpu, ArrowRight, CheckCircle, Shield, Award } from 'lucide-react';
import { Navbar } from '../components/common/Navbar';
import { Footer } from '../components/common/Footer';

export const LandingPage = () => {
  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
      <Navbar />
      
      {/* Hero Section */}
      <section className="relative py-24 px-6 max-w-7xl mx-auto text-center space-y-8 overflow-hidden">
        <div className="inline-flex items-center space-x-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-400 text-sm font-semibold">
          <Sparkles className="w-4 h-4" />
          <span>Next-Generation AI Intelligence Platform v1.0</span>
        </div>
        
        <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight leading-tight">
          Accelerate Breakthroughs with <br />
          <span className="gradient-text">AI Innovation & Grant Intelligence</span>
        </h1>
        
        <p className="max-w-3xl mx-auto text-lg text-slate-400 font-normal leading-relaxed">
          Unite researchers, university TTOs, startups, and innovation directors. Discover multi-million dollar funding grants, compute automated innovation scores, track patent landscapes, and unlock licensing opportunities.
        </p>

        <div className="flex flex-col sm:flex-row justify-center gap-4 pt-4">
          <Link
            to="/register"
            className="px-8 py-4 rounded-xl font-bold text-white gradient-bg-accent shadow-xl shadow-blue-500/25 hover:opacity-95 transition-all flex items-center justify-center space-x-2 text-base"
          >
            <span>Launch Free Trial</span>
            <ArrowRight className="w-5 h-5" />
          </Link>
          <Link
            to="/login"
            className="px-8 py-4 rounded-xl font-bold text-slate-200 bg-slate-900 border border-slate-800 hover:border-slate-700 transition-all flex items-center justify-center text-base"
          >
            Sign In to Dashboard
          </Link>
        </div>

        {/* Feature Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-16 text-left">
          <div className="glass-card p-6 space-y-3">
            <div className="w-12 h-12 rounded-xl bg-blue-500/20 text-blue-400 flex items-center justify-center font-bold">
              <Search className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold">Smart Funding Matching</h3>
            <p className="text-sm text-slate-400">Algorithmic eligibility matching connecting research keywords directly with federal, private, and international grants.</p>
          </div>

          <div className="glass-card p-6 space-y-3">
            <div className="w-12 h-12 rounded-xl bg-teal-500/20 text-teal-400 flex items-center justify-center font-bold">
              <Gauge className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold">Multi-Factor Innovation Score</h3>
            <p className="text-sm text-slate-400">Calculate quantitative scores combining research novelty, patent strength, TRL maturity, market potential, and funding relevance.</p>
          </div>

          <div className="glass-card p-6 space-y-3">
            <div className="w-12 h-12 rounded-xl bg-purple-500/20 text-purple-400 flex items-center justify-center font-bold">
              <Cpu className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold">Patent & Tech Landscape</h3>
            <p className="text-sm text-slate-400">Track 500+ patents, citation networks, emerging technology radar trends, and commercial licensing opportunities.</p>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};
