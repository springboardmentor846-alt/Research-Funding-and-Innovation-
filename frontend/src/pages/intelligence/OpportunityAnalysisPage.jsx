import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  Compass, TrendingUp, Layers, Lightbulb, Sparkles,
  ArrowRight, ShieldCheck, DollarSign, Target, CheckCircle2
} from 'lucide-react'
import { technologyService } from '@/services/technologyService'
import toast from 'react-hot-toast'

export default function OpportunityAnalysisPage() {
  const [data, setData] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchOpportunities()
  }, [])

  const fetchOpportunities = async () => {
    try {
      setIsLoading(true)
      const res = await technologyService.getOpportunities(8)
      setData(res)
    } catch (err) {
      toast.error('Failed to load opportunity analysis.')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <div className="w-12 h-12 rounded-full border-4 border-brand-500 border-t-transparent animate-spin" />
        <p className="text-surface-400 text-sm animate-pulse">Analyzing Market Opportunity Gaps...</p>
      </div>
    )
  }

  const { total_opportunities, high_alignment_count, top_domains, opportunities } = data || {}

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* ── Header ── */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 glass p-6 rounded-2xl border border-white/10">
        <div>
          <div className="flex items-center gap-2 text-accent-400 font-semibold text-xs tracking-wider uppercase mb-1">
            <Compass className="w-4 h-4" /> Market Gap & Strategic Commercialization
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white">Opportunity Analysis</h1>
          <p className="text-surface-400 text-sm mt-1">
            Identify high-value technology market gaps, target market sizes ($B), and recommended R&D commercialization actions.
          </p>
        </div>

        <Link to="/technology-intelligence/trends" className="btn-primary text-xs py-2.5 px-4 shadow-glow-brand self-start md:self-center">
          Explore Tech Trends →
        </Link>
      </div>

      {/* ── Summary Stats ── */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="glass p-5 rounded-2xl border border-white/5 space-y-1">
          <p className="text-xs text-surface-400 font-medium">Total Opportunities Identified</p>
          <p className="text-3xl font-extrabold text-white">{total_opportunities || 0}</p>
          <span className="text-[10px] text-surface-500">Market Gap Gaps</span>
        </div>

        <div className="glass p-5 rounded-2xl border border-white/5 space-y-1">
          <p className="text-xs text-surface-400 font-medium">High Profile Alignment</p>
          <p className="text-3xl font-extrabold text-accent-400">{high_alignment_count || 0}</p>
          <span className="text-[10px] text-accent-500/80 font-medium">&gt; 85% Relevance Match</span>
        </div>

        <div className="glass p-5 rounded-2xl border border-white/5 space-y-1">
          <p className="text-xs text-surface-400 font-medium">Target Tech Domains</p>
          <p className="text-3xl font-extrabold text-brand-300">{top_domains?.length || 0}</p>
          <span className="text-[10px] text-surface-500">Core Domain Alignment</span>
        </div>
      </div>

      {/* ── Opportunity Cards Grid ── */}
      <div className="space-y-4">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <Target className="w-5 h-5 text-accent-400" />
          High-Priority Commercial Opportunity Gaps
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {opportunities?.map((opp) => (
            <div
              key={opp.id}
              className="glass p-6 rounded-2xl border border-white/10 hover:border-accent-500/30 transition-all flex flex-col justify-between group space-y-4"
            >
              <div className="space-y-3">
                {/* Header Badge */}
                <div className="flex items-center justify-between gap-2">
                  <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-surface-900 text-surface-300 border border-white/10">
                    {opp.technology_domain}
                  </span>
                  <div className="flex items-center gap-1 px-2.5 py-1 rounded-full bg-accent-500/20 text-accent-300 text-xs font-bold border border-accent-500/30">
                    <Sparkles className="w-3.5 h-3.5" />
                    {opp.alignment_score}% Profile Match
                  </div>
                </div>

                {/* Title */}
                <h3 className="text-lg font-bold text-white group-hover:text-accent-300 transition-colors">
                  {opp.title}
                </h3>

                {/* Market Stats */}
                <div className="flex items-center gap-4 text-xs text-surface-400 pt-1">
                  <span>Market Size: <strong className="text-white">${opp.market_size_usd_b}B</strong></span>
                  <span>Growth Velocity: <strong className="text-emerald-400">+{opp.growth_rate}%/yr</strong></span>
                </div>

                {/* Opportunity Gap */}
                <div className="p-3 bg-surface-900/90 rounded-xl border border-white/5 space-y-1">
                  <span className="text-[10px] text-amber-400 font-bold uppercase tracking-wider block">Market Gap</span>
                  <p className="text-xs text-surface-300 leading-relaxed">
                    {opp.opportunity_gap}
                  </p>
                </div>

                {/* Actionable Strategy */}
                <div className="p-3 bg-brand-950/40 rounded-xl border border-brand-500/20 space-y-1">
                  <span className="text-[10px] text-brand-400 font-bold uppercase tracking-wider block">Recommended Action</span>
                  <p className="text-xs text-brand-200 font-medium">
                    💡 {opp.recommended_action}
                  </p>
                </div>
              </div>

              {/* Keywords */}
              <div className="pt-3 border-t border-white/5 flex flex-wrap gap-1.5">
                {opp.key_keywords?.map((kw, i) => (
                  <span key={i} className="text-[10px] bg-surface-900 text-surface-400 px-2 py-0.5 rounded border border-white/5">
                    #{kw}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
