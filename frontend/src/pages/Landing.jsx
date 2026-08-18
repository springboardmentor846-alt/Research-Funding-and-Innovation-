import React from "react";
import { Link } from "react-router-dom";

export default function Landing() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
      {/* Header */}
      <header className="px-6 py-5 flex items-center justify-between max-w-7xl mx-auto">
        <div className="flex items-center space-x-2">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center font-bold">
            R
          </div>
          <div>
            <div className="font-bold">Research Platform</div>
            <div className="text-xs text-slate-400">AI-Powered</div>
          </div>
        </div>
        <div className="space-x-2">
          <Link to="/login" className="btn-ghost text-white">Login</Link>
          <Link to="/register" className="btn-primary">Get Started</Link>
        </div>
      </header>

      {/* Hero */}
      <section className="max-w-7xl mx-auto px-6 py-20 text-center">
        <div className="inline-block mb-4 px-3 py-1 rounded-full bg-primary-500/10 border border-primary-500/30 text-primary-300 text-sm">
          🎓 Final-Year CSE Capstone Project
        </div>
        <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight">
          Research Funding &<br />
          <span className="bg-gradient-to-r from-primary-400 to-accent-500 bg-clip-text text-transparent">
            Innovation Intelligence
          </span>
        </h1>
        <p className="mt-6 text-lg text-slate-300 max-w-2xl mx-auto">
          AI-powered platform that recommends funding opportunities, analyzes patents,
          detects research trends, and unlocks commercialization insights — all in one place.
        </p>
        <div className="mt-10 flex flex-wrap gap-4 justify-center">
          <Link to="/register" className="btn-primary text-base px-6 py-3">Create Free Account →</Link>
          <Link to="/login" className="btn-secondary text-base px-6 py-3">Login</Link>
        </div>
      </section>

      {/* Features */}
      <section className="max-w-7xl mx-auto px-6 py-16">
        <h2 className="text-3xl font-bold text-center mb-12">Everything You Need to Get Funded</h2>
        <div className="grid md:grid-cols-3 gap-6">
          {[
            { icon: "🎯", title: "Smart Funding Recommendations", desc: "TF-IDF + Cosine similarity matches you with grants that fit your publications." },
            { icon: "🔬", title: "Patent Intelligence", desc: "Search across Google Patents, USPTO & The Lens with AI-powered summaries." },
            { icon: "📈", title: "Research Trend Analysis", desc: "Detect emerging topics and visualize your research growth." },
            { icon: "🤖", title: "AI Research Assistant", desc: "Summarize papers, explain patents, suggest research directions." },
            { icon: "🔍", title: "Semantic Search", desc: "Find publications, funding, and patents using Elasticsearch + FAISS." },
            { icon: "📊", title: "Innovation Dashboard", desc: "Track publications, citations, innovation score, and commercialization score." },
          ].map((f) => (
            <div key={f.title} className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 hover:border-primary-500 transition">
              <div className="text-4xl mb-3">{f.icon}</div>
              <h3 className="font-semibold text-lg mb-2">{f.title}</h3>
              <p className="text-slate-400 text-sm">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Demo Accounts */}
      <section className="max-w-7xl mx-auto px-6 py-16">
        <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-8">
          <h3 className="text-2xl font-bold mb-2">Try the Demo</h3>
          <p className="text-slate-400 mb-6">Use any of the pre-created accounts to explore the platform.</p>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
            {[
              { role: "Researcher", email: "researcher@demo.com", pass: "Research@2026" },
              { role: "Startup Founder", email: "founder@demo.com", pass: "Startup@2026" },
              { role: "Innovation Manager", email: "innovation@demo.com", pass: "Innovate@2026" },
              { role: "Admin", email: "admin@demo.com", pass: "Admin@2026" },
            ].map((a) => (
              <div key={a.email} className="bg-slate-900 rounded-lg p-4 border border-slate-700">
                <div className="font-semibold text-primary-300 mb-1">{a.role}</div>
                <div className="text-slate-400 text-xs break-all">{a.email}</div>
                <div className="text-slate-500 text-xs break-all">pw: {a.pass}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <footer className="border-t border-slate-800 mt-12 py-6 text-center text-slate-500 text-sm">
        © 2026 Research Funding & Innovation Intelligence Platform · Built with FastAPI, React, and AI
      </footer>
    </div>
  );
}
