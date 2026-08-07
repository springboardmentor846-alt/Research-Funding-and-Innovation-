import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  BrainCircuit, Sparkles, TrendingUp, BookOpen, Search, ArrowRight,
  Award, Globe, Layers, BarChart2, CheckCircle2, ShieldCheck, Zap
} from 'lucide-react'
import toast from 'react-hot-toast'
import { researchIntelligenceService } from '@/services/researchIntelligenceService'
import { clsx } from 'clsx'

export default function ResearchIntelligenceDashboardPage() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboard()
  }, [])

  const loadDashboard = async () => {
    try {
      setLoading(true)
      const res = await researchIntelligenceService.getDashboardSummary()
      setData(res)
    } catch (err) {
      toast.error('Failed to load Research Intelligence dashboard')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="w-10 h-10 border-4 border-brand-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* ── Header ── */}
      <div className="relative glass p-8 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-brand-600/10 to-accent-600/5 pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <span className="badge badge-brand mb-2">Phase 4 — Research Intelligence</span>
            <h1 className="text-2xl md:text-3xl font-extrabold text-white">
              Scientific Literature & Trend Intelligence
            </h1>
            <p className="text-surface-400 text-sm mt-1 max-w-2xl">
              AI-driven publication tracking, citation dynamics, and emerging domain trends cross-referenced with your Research Profile.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Link to="/research-intelligence/search" className="btn-primary">
              <Search className="w-4 h-4" /> Search 100+ Papers
            </Link>
            <Link to="/research-intelligence/trends" className="btn-secondary">
              <TrendingUp className="w-4 h-4" /> Explore Trends
            </Link>
          </div>
        </div>
      </div>

      {/* ── Stat Cards ── */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="glass p-5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-brand-500/20 text-brand-400 flex items-center justify-center">
            <BookOpen className="w-6 h-6" />
          </div>
          <div>
            <p className="text-2xl font-bold text-white">{data?.statistics?.total_papers_indexed || 0}</p>
            <p className="text-xs text-surface-400">Papers Indexed</p>
          </div>
        </div>

        <div className="glass p-5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-accent-500/20 text-accent-400 flex items-center justify-center">
            <Award className="w-6 h-6" />
          </div>
          <div>
            <p className="text-2xl font-bold text-white">{data?.statistics?.total_citations_tracked || 0}</p>
            <p className="text-xs text-surface-400">Total Citations</p>
          </div>
        </div>

        <div className="glass p-5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-green-500/20 text-green-400 flex items-center justify-center">
            <TrendingUp className="w-6 h-6" />
          </div>
          <div>
            <p className="text-2xl font-bold text-white">{data?.statistics?.trending_topics_count || 0}</p>
            <p className="text-xs text-surface-400">Trending Topics</p>
          </div>
        </div>

        <div className="glass p-5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-orange-500/20 text-orange-400 flex items-center justify-center">
            <Layers className="w-6 h-6" />
          </div>
          <div>
            <p className="text-2xl font-bold text-white">3 Providers</p>
            <p className="text-xs text-surface-400">OpenAlex / Semantic Ready</p>
          </div>
        </div>
      </div>

      {/* ── Section 1: AI Recommended Papers ── */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-brand-400" />
            <h2 className="text-xl font-bold text-white">Recommended Papers For You</h2>
          </div>
          <Link to="/research-intelligence/search" className="text-xs font-semibold text-brand-400 hover:text-brand-300 flex items-center gap-1">
            Search All Papers <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="grid md:grid-cols-2 gap-5">
          {data?.recommended_papers?.map((item) => {
            const paper = item.paper
            return (
              <div key={paper.id} className="glass p-6 flex flex-col justify-between hover:border-brand-500/40 transition-all">
                <div className="space-y-3">
                  <div className="flex items-center justify-between gap-3">
                    <span className="badge badge-brand text-xs">
                      {item.match_score}% Match Score
                    </span>
                    <span className="text-xs text-surface-400">
                      {paper.citations_count} citations
                    </span>
                  </div>

                  <Link to={`/research-intelligence/paper/${paper.id}`} className="block group">
                    <h3 className="text-base font-bold text-white group-hover:text-brand-300 transition-colors line-clamp-2">
                      {paper.title}
                    </h3>
                  </Link>

                  <p className="text-xs font-medium text-surface-400 truncate">
                    {paper.authors?.join(', ')} • <span className="text-surface-300">{paper.venue} ({paper.publication_year})</span>
                  </p>

                  <p className="text-xs text-surface-300 line-clamp-3">{paper.abstract}</p>

                  {/* Recommendation Reason Box */}
                  <div className="p-3 bg-brand-500/10 border border-brand-500/20 rounded-xl text-xs text-brand-300 flex items-start gap-2">
                    <Zap className="w-4 h-4 text-brand-400 flex-shrink-0 mt-0.5" />
                    <span>{item.matching_reason}</span>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-white/5 flex items-center justify-between text-xs">
                  <div className="flex gap-1.5">
                    {paper.research_domains?.slice(0, 2).map((d) => (
                      <span key={d} className="badge bg-white/5 text-surface-300 text-[10px]">
                        {d}
                      </span>
                    ))}
                  </div>
                  <Link to={`/research-intelligence/paper/${paper.id}`} className="text-brand-400 font-semibold hover:underline">
                    Read Paper →
                  </Link>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* ── Section 2: Trending & Emerging Topics ── */}
      <div className="grid md:grid-cols-2 gap-8">
        {/* Trending */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-green-400" /> Top Trending Domains
            </h2>
            <Link to="/research-intelligence/trends" className="text-xs text-brand-400 hover:underline">
              View All
            </Link>
          </div>

          <div className="space-y-3">
            {data?.trending_topics?.map((t) => (
              <div key={t.id} className="glass p-4 flex items-center justify-between">
                <div className="min-w-0 pr-3">
                  <h4 className="text-sm font-bold text-white truncate">{t.topic_name}</h4>
                  <p className="text-xs text-surface-400 mt-0.5">{t.research_domain} • {t.paper_count} papers</p>
                </div>
                <span className="badge badge-green flex-shrink-0 text-xs font-bold">
                  +{t.growth_rate}%
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Emerging */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Zap className="w-5 h-5 text-accent-400" /> Emerging Breakthroughs
            </h2>
            <Link to="/research-intelligence/trends" className="text-xs text-brand-400 hover:underline">
              View All
            </Link>
          </div>

          <div className="space-y-3">
            {data?.emerging_topics?.map((t) => (
              <div key={t.id} className="glass p-4 flex items-center justify-between">
                <div className="min-w-0 pr-3">
                  <h4 className="text-sm font-bold text-white truncate">{t.topic_name}</h4>
                  <p className="text-xs text-surface-400 mt-0.5">{t.research_domain} • {t.paper_count} papers</p>
                </div>
                <span className="badge badge-accent flex-shrink-0 text-xs font-bold">
                  +{t.growth_rate}%
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
