import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  Cpu, TrendingUp, Award, Compass, Search, Sparkles,
  Layers, ChevronRight, Gauge, Lightbulb, Rocket, Zap
} from 'lucide-react'
import { technologyService } from '@/services/technologyService'
import toast from 'react-hot-toast'

export default function TechnologyDashboardPage() {
  const [data, setData] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setIsLoading(true)
      const summary = await technologyService.getDashboardSummary()
      setData(summary)
    } catch (err) {
      toast.error('Failed to load technology intelligence dashboard.')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <div className="w-12 h-12 rounded-full border-4 border-brand-500 border-t-transparent animate-spin" />
        <p className="text-surface-400 text-sm animate-pulse">Calculating Technology Intelligence...</p>
      </div>
    )
  }

  const { statistics, emerging_technologies, innovation_score, recommended_opportunities } = data || {}

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* ── Header ── */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 glass p-6 rounded-2xl border border-white/10">
        <div>
          <div className="flex items-center gap-2 text-brand-400 font-semibold text-xs tracking-wider uppercase mb-1">
            <Cpu className="w-4 h-4" /> Phase 6 · Technology Intelligence & Innovation Scoring
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white">Technology Dashboard</h1>
          <p className="text-surface-400 text-sm mt-1">
            Discover emerging tech trends, evaluate your Technology Readiness Level (TRL), and analyze high-growth commercial opportunities.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to="/technology-intelligence/trends"
            className="btn-secondary flex items-center gap-2 text-sm"
          >
            <Search className="w-4 h-4" />
            Tech Trends
          </Link>
          <Link
            to="/technology-intelligence/innovation-score"
            className="btn-primary flex items-center gap-2 text-sm shadow-glow-brand"
          >
            <Award className="w-4 h-4" />
            Innovation Score
          </Link>
        </div>
      </div>

      {/* ── Key Technology Statistics ── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass p-5 rounded-2xl border border-white/5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-brand-500/20 text-brand-400 flex items-center justify-center flex-shrink-0">
            <Cpu className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs text-surface-400 font-medium">Total Tech Trends</p>
            <p className="text-2xl font-bold text-white mt-0.5">{statistics?.total_trends_indexed || 0}</p>
            <span className="text-[10px] text-surface-500">Indexed Tech Domains</span>
          </div>
        </div>

        <div className="glass p-5 rounded-2xl border border-white/5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center flex-shrink-0">
            <Zap className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs text-surface-400 font-medium">Emerging Techs</p>
            <p className="text-2xl font-bold text-emerald-400 mt-0.5">{statistics?.emerging_count || 0}</p>
            <span className="text-[10px] text-emerald-500/80 font-medium">High Growth Drivers</span>
          </div>
        </div>

        <div className="glass p-5 rounded-2xl border border-white/5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-amber-500/20 text-amber-400 flex items-center justify-center flex-shrink-0">
            <TrendingUp className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs text-surface-400 font-medium">Avg Annual Growth</p>
            <p className="text-2xl font-bold text-amber-400 mt-0.5">+{statistics?.avg_growth_rate || 0}%</p>
            <span className="text-[10px] text-amber-500/80 font-medium">Market Velocity</span>
          </div>
        </div>

        <div className="glass p-5 rounded-2xl border border-white/5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-accent-500/20 text-accent-400 flex items-center justify-center flex-shrink-0">
            <Layers className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs text-surface-400 font-medium">Leading Domain</p>
            <p className="text-sm font-bold text-accent-300 mt-1 line-clamp-1">{statistics?.top_tech_domain || 'Artificial Intelligence'}</p>
            <span className="text-[10px] text-surface-500">Highest Market Expansion</span>
          </div>
        </div>
      </div>

      {/* ── User Innovation Score Widget Card ── */}
      {innovation_score && (
        <div className="glass p-6 rounded-2xl border border-white/10 bg-gradient-to-r from-brand-950/40 via-surface-900 to-accent-950/30 space-y-6">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
            <div className="space-y-2 max-w-2xl">
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-accent-400 animate-pulse" />
                <span className="text-xs font-bold uppercase tracking-wider text-accent-400">Your Innovation Profile</span>
              </div>
              <h2 className="text-xl md:text-2xl font-extrabold text-white">
                Innovation Score: <span className="gradient-text">{innovation_score.overall_score} / 100</span>
              </h2>
              <p className="text-xs text-surface-300 leading-relaxed">
                {innovation_score.recommendation_summary}
              </p>
            </div>

            {/* Score Badges */}
            <div className="flex flex-wrap items-center gap-4">
              <div className="glass p-4 rounded-xl border border-white/10 text-center min-w-[110px]">
                <span className="text-[10px] text-surface-400 font-medium block">TRL Level</span>
                <span className="text-2xl font-extrabold text-brand-300">TRL-{innovation_score.trl_level}</span>
                <span className="text-[9px] text-surface-500 block">System Prototype</span>
              </div>

              <div className="glass p-4 rounded-xl border border-white/10 text-center min-w-[110px]">
                <span className="text-[10px] text-surface-400 font-medium block">Research</span>
                <span className="text-2xl font-extrabold text-emerald-400">{innovation_score.research_strength}</span>
                <span className="text-[9px] text-emerald-500/80 block">Paper & Citation Index</span>
              </div>

              <div className="glass p-4 rounded-xl border border-white/10 text-center min-w-[110px]">
                <span className="text-[10px] text-surface-400 font-medium block">Patent Power</span>
                <span className="text-2xl font-extrabold text-amber-400">{innovation_score.patent_strength}</span>
                <span className="text-[9px] text-amber-500/80 block">IP Portfolio</span>
              </div>

              <Link
                to="/technology-intelligence/innovation-score"
                className="btn-secondary text-xs py-2 px-3 flex items-center gap-1.5 self-center"
              >
                Full Score Details <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        </div>
      )}

      {/* ── Emerging Technologies & Opportunities Grid ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Emerging Technologies */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Zap className="w-5 h-5 text-emerald-400" />
              <h2 className="text-xl font-bold text-white">Emerging Technologies</h2>
            </div>
            <Link to="/technology-intelligence/trends" className="text-xs text-brand-400 hover:underline">
              View All Trends →
            </Link>
          </div>

          <div className="space-y-3">
            {emerging_technologies?.map((tech) => (
              <div key={tech.id} className="glass p-4 rounded-xl border border-white/5 space-y-2 hover:border-brand-500/30 transition-all">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-white line-clamp-1">{tech.name}</h3>
                  <span className="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-2.5 py-0.5 rounded-full border border-emerald-500/20 whitespace-nowrap">
                    +{tech.growth_rate}% Growth
                  </span>
                </div>
                <p className="text-xs text-surface-400 line-clamp-2">{tech.summary}</p>
                <div className="flex items-center justify-between text-[11px] text-surface-400 pt-1">
                  <span className="text-brand-300 font-semibold">{tech.maturity_level}</span>
                  <span className="text-surface-500">Market: ${tech.market_size_usd_b}B</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recommended Opportunities */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Compass className="w-5 h-5 text-accent-400" />
              <h2 className="text-xl font-bold text-white">Recommended Opportunities</h2>
            </div>
            <Link to="/technology-intelligence/opportunities" className="text-xs text-accent-400 hover:underline">
              Full Gap Analysis →
            </Link>
          </div>

          <div className="space-y-3">
            {recommended_opportunities?.map((opp) => (
              <div key={opp.id} className="glass p-4 rounded-xl border border-white/5 space-y-2 hover:border-accent-500/30 transition-all">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-white line-clamp-1">{opp.title}</h3>
                  <span className="text-xs font-bold text-accent-300 bg-accent-500/10 px-2.5 py-0.5 rounded-full border border-accent-500/20">
                    {opp.alignment_score}% Match
                  </span>
                </div>
                <p className="text-xs text-surface-400 line-clamp-2">{opp.opportunity_gap}</p>
                <div className="p-2 bg-surface-900/80 rounded-lg border border-white/5 text-[11px] text-brand-300 font-medium">
                  💡 {opp.recommended_action}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
