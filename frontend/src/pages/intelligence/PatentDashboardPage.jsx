import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  Lightbulb, Search, BarChart3, TrendingUp, Building2,
  FileCheck, ShieldCheck, Clock, Sparkles, ExternalLink,
  ChevronRight, Award, Layers
} from 'lucide-react'
import { patentService } from '@/services/patentService'
import toast from 'react-hot-toast'

export default function PatentDashboardPage() {
  const [data, setData] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setIsLoading(true)
      const summary = await patentService.getDashboardSummary()
      setData(summary)
    } catch (err) {
      toast.error('Failed to load patent intelligence dashboard.')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <div className="w-12 h-12 rounded-full border-4 border-brand-500 border-t-transparent animate-spin" />
        <p className="text-surface-400 text-sm animate-pulse">Loading Patent Intelligence...</p>
      </div>
    )
  }

  const { statistics, recent_patents, top_organizations, trending_technologies, recommendations } = data || {}

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* ── Header ── */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 glass p-6 rounded-2xl border border-white/10">
        <div>
          <div className="flex items-center gap-2 text-brand-400 font-semibold text-xs tracking-wider uppercase mb-1">
            <Lightbulb className="w-4 h-4" /> Phase 5 · Patent Intelligence & IP Analytics
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white">Global Patent Dashboard</h1>
          <p className="text-surface-400 text-sm mt-1">
            Track patent filings, analyze technology domain trends, evaluate assignees, and discover AI-matched IP.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to="/patent-intelligence/search"
            className="btn-secondary flex items-center gap-2 text-sm"
          >
            <Search className="w-4 h-4" />
            Patent Search
          </Link>
          <Link
            to="/patent-intelligence/analytics"
            className="btn-primary flex items-center gap-2 text-sm shadow-glow-brand"
          >
            <BarChart3 className="w-4 h-4" />
            Patent Analytics
          </Link>
        </div>
      </div>

      {/* ── Key Statistics Cards ── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass p-5 rounded-2xl border border-white/5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-brand-500/20 text-brand-400 flex items-center justify-center flex-shrink-0">
            <FileCheck className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs text-surface-400 font-medium">Total Patents Indexed</p>
            <p className="text-2xl font-bold text-white mt-0.5">{statistics?.total_patents_indexed || 0}</p>
            <span className="text-[10px] text-surface-500">Global Records Database</span>
          </div>
        </div>

        <div className="glass p-5 rounded-2xl border border-white/5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center flex-shrink-0">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs text-surface-400 font-medium">Granted Patents</p>
            <p className="text-2xl font-bold text-emerald-400 mt-0.5">{statistics?.granted_count || 0}</p>
            <span className="text-[10px] text-emerald-500/80 font-medium">Active Enforceable IP</span>
          </div>
        </div>

        <div className="glass p-5 rounded-2xl border border-white/5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-amber-500/20 text-amber-400 flex items-center justify-center flex-shrink-0">
            <Clock className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs text-surface-400 font-medium">Pending Applications</p>
            <p className="text-2xl font-bold text-amber-400 mt-0.5">{statistics?.pending_count || 0}</p>
            <span className="text-[10px] text-amber-500/80 font-medium">Under Examination</span>
          </div>
        </div>

        <div className="glass p-5 rounded-2xl border border-white/5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-accent-500/20 text-accent-400 flex items-center justify-center flex-shrink-0">
            <Layers className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs text-surface-400 font-medium">Top Tech Domain</p>
            <p className="text-sm font-bold text-accent-300 mt-1 line-clamp-1">{statistics?.top_domain || 'Artificial Intelligence'}</p>
            <span className="text-[10px] text-surface-500">Highest Filing Density</span>
          </div>
        </div>
      </div>

      {/* ── AI Patent Recommendations Section ── */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-accent-400 animate-pulse" />
            <h2 className="text-xl font-bold text-white">AI Patent Recommendations</h2>
          </div>
          <span className="text-xs text-surface-400">Matched with your Research Profile</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {recommendations?.map((rec) => (
            <div
              key={rec.id}
              className="glass p-5 rounded-2xl border border-white/10 hover:border-brand-500/30 transition-all flex flex-col justify-between group"
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-2">
                  <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-brand-500/20 text-brand-300 border border-brand-500/30">
                    {rec.patent_number}
                  </span>
                  <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-accent-500/20 text-accent-300 text-xs font-bold border border-accent-500/30">
                    <Sparkles className="w-3.5 h-3.5" />
                    {rec.match_score}% Match
                  </div>
                </div>

                <Link
                  to={`/patent-intelligence/${rec.id}`}
                  className="text-base font-bold text-white group-hover:text-brand-300 transition-colors line-clamp-2"
                >
                  {rec.title}
                </Link>

                <p className="text-xs text-surface-400 mt-2 line-clamp-2">{rec.abstract}</p>

                {/* Matching Badges */}
                <div className="flex flex-wrap gap-1.5 mt-3">
                  {rec.matching_fields?.map((field, idx) => (
                    <span key={idx} className="text-[10px] px-2 py-0.5 rounded bg-surface-800 text-surface-300 border border-white/5">
                      ✓ {field}
                    </span>
                  ))}
                </div>

                <p className="text-[11px] text-brand-400/90 italic mt-2 line-clamp-2">
                  "{rec.recommendation_reason}"
                </p>
              </div>

              <div className="flex items-center justify-between pt-4 mt-4 border-t border-white/5 text-xs text-surface-400">
                <span className="truncate max-w-[180px]"><Building2 className="w-3.5 h-3.5 inline mr-1 text-surface-500" />{rec.assignee_organization}</span>
                <Link
                  to={`/patent-intelligence/${rec.id}`}
                  className="text-brand-400 hover:text-brand-300 font-medium inline-flex items-center gap-1"
                >
                  View Details <ChevronRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── Trending Technologies & Top Assignees Grid ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Trending Technologies (2 cols) */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-emerald-400" />
              <h2 className="text-xl font-bold text-white">Trending Patent Technologies</h2>
            </div>
            <Link to="/patent-intelligence/analytics" className="text-xs text-brand-400 hover:underline">
              View Analytics →
            </Link>
          </div>

          <div className="space-y-3">
            {trending_technologies?.map((trend) => (
              <div key={trend.id} className="glass p-4 rounded-xl border border-white/5 space-y-2">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-white">{trend.technology_domain}</h3>
                  <span className="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/20">
                    +{trend.growth_rate}% Annual Growth
                  </span>
                </div>
                <p className="text-xs text-surface-400 line-clamp-2">{trend.summary}</p>
                <div className="flex flex-wrap items-center gap-2 text-[11px] text-surface-400 pt-1">
                  <span className="text-surface-500">Key Assignees:</span>
                  {trend.top_assignees?.slice(0, 3).map((org, i) => (
                    <span key={i} className="bg-surface-800 text-surface-300 px-2 py-0.5 rounded text-[10px]">
                      {org}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top Organizations (1 col) */}
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <Building2 className="w-5 h-5 text-brand-400" />
            <h2 className="text-xl font-bold text-white">Top Assignees</h2>
          </div>

          <div className="glass p-5 rounded-2xl border border-white/5 space-y-4">
            {top_organizations?.map((org, idx) => (
              <div key={idx} className="space-y-1.5">
                <div className="flex justify-between items-center text-xs">
                  <span className="font-semibold text-surface-200 truncate max-w-[180px]">
                    {idx + 1}. {org.name}
                  </span>
                  <span className="text-brand-400 font-bold">{org.count} patents</span>
                </div>
                <div className="w-full bg-surface-800 rounded-full h-1.5 overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-brand-500 to-accent-500 h-full rounded-full"
                    style={{ width: `${Math.max(org.percentage * 3, 10)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Recent Patent Filings ── */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Clock className="w-5 h-5 text-amber-400" />
            <h2 className="text-xl font-bold text-white">Recent Patent Filings</h2>
          </div>
          <Link to="/patent-intelligence/search" className="text-xs text-brand-400 hover:underline">
            View All Patents ({statistics?.total_patents_indexed}) →
          </Link>
        </div>

        <div className="glass rounded-2xl border border-white/5 overflow-hidden">
          <div className="divide-y divide-white/5">
            {recent_patents?.map((pat) => (
              <div key={pat.id} className="p-4 hover:bg-white/[0.02] transition-colors flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="space-y-1 max-w-3xl">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono font-bold text-brand-300">{pat.patent_number}</span>
                    <span className={`text-[10px] px-2 py-0.5 rounded-full font-semibold ${
                      pat.status === 'Granted' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' :
                      pat.status === 'Pending' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                      'bg-surface-800 text-surface-400'
                    }`}>
                      {pat.status}
                    </span>
                    <span className="text-xs text-surface-500">· Published {pat.publication_date}</span>
                  </div>
                  <Link to={`/patent-intelligence/${pat.id}`} className="text-sm font-bold text-white hover:text-brand-300 transition-colors block">
                    {pat.title}
                  </Link>
                  <p className="text-xs text-surface-400 flex items-center gap-2">
                    <span><Building2 className="w-3 h-3 inline mr-1" />{pat.assignee_organization}</span>
                    <span>· Domain: {pat.technology_domain}</span>
                  </p>
                </div>

                <Link
                  to={`/patent-intelligence/${pat.id}`}
                  className="btn-secondary text-xs py-1.5 px-3 whitespace-nowrap self-start sm:self-center"
                >
                  View Patent
                </Link>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
