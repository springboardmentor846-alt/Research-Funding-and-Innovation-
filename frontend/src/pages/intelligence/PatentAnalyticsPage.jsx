import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  BarChart3, Building2, Layers, Calendar, ShieldCheck,
  TrendingUp, PieChart, Award, FileCheck, ArrowRight
} from 'lucide-react'
import { patentService } from '@/services/patentService'
import toast from 'react-hot-toast'

export default function PatentAnalyticsPage() {
  const [analytics, setAnalytics] = useState(null)
  const [trends, setTrends] = useState([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchAnalyticsData()
  }, [])

  const fetchAnalyticsData = async () => {
    try {
      setIsLoading(true)
      const [analyticsRes, trendsRes] = await Promise.all([
        patentService.getAnalytics(),
        patentService.getTrends(8),
      ])
      setAnalytics(analyticsRes)
      setTrends(trendsRes)
    } catch (err) {
      toast.error('Failed to load patent analytics.')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <div className="w-12 h-12 rounded-full border-4 border-brand-500 border-t-transparent animate-spin" />
        <p className="text-surface-400 text-sm animate-pulse">Calculating Patent Analytics...</p>
      </div>
    )
  }

  const {
    total_patents,
    granted_patents,
    pending_patents,
    expired_patents,
    top_organizations,
    technology_domains,
    publication_years,
    status_distribution,
  } = analytics || {}

  const maxYearCount = Math.max(...(publication_years?.map((y) => y.count) || [1]))

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* ── Header ── */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 glass p-6 rounded-2xl border border-white/10">
        <div>
          <div className="flex items-center gap-2 text-brand-400 font-semibold text-xs tracking-wider uppercase mb-1">
            <BarChart3 className="w-4 h-4" /> Patent Intelligence & Landscape Analytics
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white">Global Patent Analytics</h1>
          <p className="text-surface-400 text-sm mt-1">
            Quantitative analysis of global patent volume, technology domain distributions, top patent assignees, and filing timelines.
          </p>
        </div>

        <Link to="/patent-intelligence/search" className="btn-primary text-xs py-2.5 px-4 shadow-glow-brand self-start md:self-center">
          Explore Patent Search →
        </Link>
      </div>

      {/* ── Overview Metrics ── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass p-5 rounded-2xl border border-white/5 space-y-1">
          <p className="text-xs text-surface-400 font-medium">Total Patent Database</p>
          <p className="text-3xl font-extrabold text-white">{total_patents}</p>
          <span className="text-[10px] text-surface-500">Indexed Inventions</span>
        </div>

        <div className="glass p-5 rounded-2xl border border-white/5 space-y-1">
          <p className="text-xs text-surface-400 font-medium">Granted Enforceable IP</p>
          <p className="text-3xl font-extrabold text-emerald-400">{granted_patents}</p>
          <span className="text-[10px] text-emerald-500/80 font-medium">
            {total_patents ? round((granted_patents / total_patents) * 100, 1) : 0}% Grant Rate
          </span>
        </div>

        <div className="glass p-5 rounded-2xl border border-white/5 space-y-1">
          <p className="text-xs text-surface-400 font-medium">Pending Applications</p>
          <p className="text-3xl font-extrabold text-amber-400">{pending_patents}</p>
          <span className="text-[10px] text-amber-500/80 font-medium">Active Examination</span>
        </div>

        <div className="glass p-5 rounded-2xl border border-white/5 space-y-1">
          <p className="text-xs text-surface-400 font-medium">Public Domain / Expired</p>
          <p className="text-3xl font-extrabold text-surface-400">{expired_patents}</p>
          <span className="text-[10px] text-surface-500">Prior Art Reference</span>
        </div>
      </div>

      {/* ── Visual Analytics Grid ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Top Patenting Organizations Leaderboard */}
        <div className="glass p-6 rounded-2xl border border-white/10 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Building2 className="w-5 h-5 text-brand-400" />
              Top Patent Assignees (Market Leaders)
            </h2>
            <span className="text-xs text-surface-400">Patents & Share</span>
          </div>

          <div className="space-y-4">
            {top_organizations?.map((org, i) => (
              <div key={i} className="space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-surface-200 truncate max-w-[240px]">
                    {i + 1}. {org.name}
                  </span>
                  <span className="text-brand-300 font-mono font-bold">
                    {org.count} patents ({org.percentage}%)
                  </span>
                </div>
                <div className="w-full bg-surface-900 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-brand-500 to-accent-500 h-full rounded-full transition-all duration-500"
                    style={{ width: `${Math.max(org.percentage * 3.5, 5)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Technology Domain Distribution */}
        <div className="glass p-6 rounded-2xl border border-white/10 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Layers className="w-5 h-5 text-accent-400" />
              Technology Domain Breakdown
            </h2>
            <span className="text-xs text-surface-400">Density</span>
          </div>

          <div className="space-y-4">
            {technology_domains?.map((dom, i) => (
              <div key={i} className="space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-surface-200 truncate max-w-[240px]">
                    {dom.domain}
                  </span>
                  <span className="text-accent-300 font-mono font-bold">
                    {dom.count} ({dom.percentage}%)
                  </span>
                </div>
                <div className="w-full bg-surface-900 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-accent-500 to-emerald-500 h-full rounded-full transition-all duration-500"
                    style={{ width: `${Math.max(dom.percentage * 3.5, 5)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Publication Year Filings Timeline ── */}
      <div className="glass p-6 rounded-2xl border border-white/10 space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Calendar className="w-5 h-5 text-amber-400" />
            Patent Publication Trend (2018 – 2025)
          </h2>
          <span className="text-xs text-surface-400">Volume per Year</span>
        </div>

        <div className="flex items-end justify-between gap-2 h-48 pt-6 px-4 border-b border-white/10">
          {publication_years?.map((yrItem) => {
            const heightPercent = Math.max(round((yrItem.count / maxYearCount) * 100, 1), 12)
            return (
              <div key={yrItem.year} className="flex-1 flex flex-col items-center gap-2 group h-full justify-end">
                <span className="text-[11px] font-mono font-bold text-brand-300 opacity-80 group-hover:opacity-100">
                  {yrItem.count}
                </span>
                <div
                  className="w-full max-w-[36px] bg-gradient-to-t from-brand-600 to-accent-500 rounded-t-lg transition-all duration-300 group-hover:from-brand-500 group-hover:to-accent-400"
                  style={{ height: `${heightPercent}%` }}
                />
                <span className="text-xs font-semibold text-surface-400 group-hover:text-white">
                  {yrItem.year}
                </span>
              </div>
            )
          })}
        </div>
      </div>

      {/* ── Emerging Technology Trends ── */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-emerald-400" />
            Emerging Innovation Intelligence
          </h2>
          <span className="text-xs text-surface-400">High Growth Rate Metrics</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {trends?.map((t) => (
            <div key={t.id} className="glass p-5 rounded-2xl border border-white/5 space-y-3 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between gap-1 mb-2">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-surface-400">
                    {t.is_emerging ? '⚡ Emerging' : '📈 Growth Domain'}
                  </span>
                  <span className="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                    +{t.growth_rate}%
                  </span>
                </div>

                <h3 className="text-sm font-bold text-white line-clamp-1">{t.technology_domain}</h3>
                <p className="text-xs text-surface-400 mt-1 line-clamp-3 leading-relaxed">{t.summary}</p>
              </div>

              <div className="pt-2 border-t border-white/5 flex flex-wrap gap-1">
                {t.key_keywords?.slice(0, 3).map((kw, i) => (
                  <span key={i} className="text-[10px] bg-surface-900 text-surface-300 px-2 py-0.5 rounded">
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

function round(value, precision) {
  const multiplier = Math.pow(10, precision || 0)
  return Math.round(value * multiplier) / multiplier
}
