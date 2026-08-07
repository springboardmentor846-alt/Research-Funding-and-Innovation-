import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  Coins, Sparkles, Clock, Bookmark, Search, ArrowRight,
  Building, Calendar, DollarSign, Globe, CheckCircle2, BookmarkCheck
} from 'lucide-react'
import toast from 'react-hot-toast'
import { fundingService } from '@/services/fundingService'
import { clsx } from 'clsx'

export default function FundingDashboardPage() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboard()
  }, [])

  const loadDashboard = async () => {
    try {
      setLoading(true)
      const res = await fundingService.getDashboardSummary()
      setData(res)
    } catch (err) {
      toast.error('Failed to load funding dashboard')
    } finally {
      setLoading(false)
    }
  }

  const handleToggleBookmark = async (oppId) => {
    try {
      const res = await fundingService.toggleBookmark(oppId)
      toast.success(res.message)
      loadDashboard()
    } catch (err) {
      toast.error('Failed to update bookmark')
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
            <span className="badge badge-brand mb-2">Phase 3 — Discovery Engine</span>
            <h1 className="text-2xl md:text-3xl font-extrabold text-white">
              Funding Intelligence & Grant Discovery
            </h1>
            <p className="text-surface-400 text-sm mt-1 max-w-2xl">
              AI-matched research grants, venture capital cohorts, and government innovation awards tailored to your profile.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Link to="/funding/search" className="btn-primary">
              <Search className="w-4 h-4" /> Explore Grants
            </Link>
            <Link to="/funding/bookmarks" className="btn-secondary">
              <Bookmark className="w-4 h-4" /> Saved Grants ({data?.saved_grants_count || 0})
            </Link>
          </div>
        </div>
      </div>

      {/* ── Stat Cards ── */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="glass p-5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-brand-500/20 text-brand-400 flex items-center justify-center">
            <Sparkles className="w-6 h-6" />
          </div>
          <div>
            <p className="text-2xl font-bold text-white">{data?.recommended_grants?.length || 0}</p>
            <p className="text-xs text-surface-400">AI Matches</p>
          </div>
        </div>

        <div className="glass p-5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-accent-500/20 text-accent-400 flex items-center justify-center">
            <Coins className="w-6 h-6" />
          </div>
          <div>
            <p className="text-2xl font-bold text-white">{data?.total_opportunities_count || 0}</p>
            <p className="text-xs text-surface-400">Total Opportunities</p>
          </div>
        </div>

        <div className="glass p-5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-orange-500/20 text-orange-400 flex items-center justify-center">
            <Clock className="w-6 h-6" />
          </div>
          <div>
            <p className="text-2xl font-bold text-white">{data?.closing_soon_grants?.length || 0}</p>
            <p className="text-xs text-surface-400">Closing Soon</p>
          </div>
        </div>

        <div className="glass p-5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-green-500/20 text-green-400 flex items-center justify-center">
            <BookmarkCheck className="w-6 h-6" />
          </div>
          <div>
            <p className="text-2xl font-bold text-white">{data?.saved_grants_count || 0}</p>
            <p className="text-xs text-surface-400">Saved Grants</p>
          </div>
        </div>
      </div>

      {/* ── Section 1: AI Recommended Grants ── */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-brand-400" />
            <h2 className="text-xl font-bold text-white">Recommended For You</h2>
          </div>
          <Link to="/funding/search" className="text-xs font-semibold text-brand-400 hover:text-brand-300 flex items-center gap-1">
            View All <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="grid md:grid-cols-2 gap-4">
          {data?.recommended_grants?.map((item) => {
            const opp = item.opportunity
            return (
              <div key={opp.id} className="glass p-5 flex flex-col justify-between hover:border-brand-500/40 transition-all">
                <div className="space-y-3">
                  <div className="flex items-start justify-between gap-3">
                    <span className="badge badge-brand text-xs">
                      {item.match_score}% Match
                    </span>
                    <button
                      onClick={() => handleToggleBookmark(opp.id)}
                      className={clsx(
                        'p-2 rounded-lg transition-colors',
                        opp.is_bookmarked
                          ? 'bg-brand-500 text-white'
                          : 'bg-white/5 text-surface-400 hover:text-white'
                      )}
                    >
                      <Bookmark className="w-4 h-4" />
                    </button>
                  </div>

                  <Link to={`/funding/${opp.id}`} className="block group">
                    <h3 className="text-base font-bold text-white group-hover:text-brand-300 transition-colors line-clamp-2">
                      {opp.title}
                    </h3>
                  </Link>

                  <div className="flex items-center gap-4 text-xs text-surface-400">
                    <span className="flex items-center gap-1">
                      <Building className="w-3.5 h-3.5 text-surface-500" /> {opp.funder_name}
                    </span>
                    <span className="flex items-center gap-1">
                      <DollarSign className="w-3.5 h-3.5 text-accent-400" />
                      {opp.amount_max ? `$${(opp.amount_max / 1000).toFixed(0)}K` : 'Varies'} {opp.currency}
                    </span>
                  </div>

                  <p className="text-xs text-surface-300 line-clamp-2">{opp.description}</p>

                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {item.matched_domains?.map((d) => (
                      <span key={d} className="badge bg-brand-500/10 text-brand-300 text-[10px]">
                        {d}
                      </span>
                    ))}
                    {item.matched_keywords?.map((k) => (
                      <span key={k} className="badge bg-accent-500/10 text-accent-300 text-[10px]">
                        #{k}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-white/5 flex items-center justify-between text-xs text-surface-400">
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3.5 h-3.5" />
                    Deadline: {opp.deadline ? new Date(opp.deadline).toLocaleDateString() : 'Rolling'}
                  </span>
                  <Link to={`/funding/${opp.id}`} className="text-brand-400 font-semibold hover:underline">
                    View Details →
                  </Link>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* ── Section 2: Closing Soon ── */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Clock className="w-5 h-5 text-orange-400" />
            <h2 className="text-xl font-bold text-white">Closing Soon</h2>
          </div>
          <Link to="/funding/search?sort_by=deadline_asc" className="text-xs font-semibold text-brand-400 hover:text-brand-300 flex items-center gap-1">
            See All Deadlines <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="grid md:grid-cols-4 gap-4">
          {data?.closing_soon_grants?.map((opp) => (
            <div key={opp.id} className="glass p-4 flex flex-col justify-between">
              <div className="space-y-2">
                <span className="badge badge-orange text-[10px]">
                  {opp.deadline ? `${Math.max(0, Math.ceil((new Date(opp.deadline) - new Date()) / (1000 * 60 * 60 * 24)))} days left` : 'Rolling'}
                </span>
                <Link to={`/funding/${opp.id}`} className="block group">
                  <h4 className="text-sm font-bold text-white group-hover:text-brand-300 transition-colors line-clamp-2">
                    {opp.title}
                  </h4>
                </Link>
                <p className="text-xs text-surface-400 truncate">{opp.funder_name}</p>
              </div>

              <div className="mt-3 pt-2 border-t border-white/5 flex items-center justify-between text-xs">
                <span className="text-accent-400 font-semibold">
                  {opp.amount_max ? `$${(opp.amount_max / 1000).toFixed(0)}K` : 'Varies'}
                </span>
                <Link to={`/funding/${opp.id}`} className="text-brand-400 hover:underline text-[11px]">
                  Apply →
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
