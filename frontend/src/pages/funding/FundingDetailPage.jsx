import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  Building, Calendar, DollarSign, Globe, Bookmark, ArrowLeft,
  ExternalLink, CheckCircle2, ShieldCheck, Tag, Sparkles
} from 'lucide-react'
import toast from 'react-hot-toast'
import { fundingService } from '@/services/fundingService'
import { clsx } from 'clsx'

export default function FundingDetailPage() {
  const { id } = useParams()
  const [opp, setOpp] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadOpportunity()
  }, [id])

  const loadOpportunity = async () => {
    try {
      setLoading(true)
      const res = await fundingService.getOpportunityDetails(id)
      setOpp(res)
    } catch (err) {
      toast.error('Failed to load funding opportunity details')
    } finally {
      setLoading(false)
    }
  }

  const handleToggleBookmark = async () => {
    try {
      const res = await fundingService.toggleBookmark(id)
      toast.success(res.message)
      setOpp((prev) => ({ ...prev, is_bookmarked: res.bookmarked }))
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

  if (!opp) {
    return (
      <div className="glass p-12 text-center space-y-4 max-w-xl mx-auto">
        <h3 className="text-xl font-bold text-white">Funding Opportunity Not Found</h3>
        <p className="text-surface-400 text-sm">The grant opportunity you are looking for may have expired or been removed.</p>
        <Link to="/funding/search" className="btn-primary text-xs">Back to Search</Link>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* ── Back button ── */}
      <Link to="/funding/search" className="inline-flex items-center gap-2 text-xs font-semibold text-surface-400 hover:text-white transition-colors">
        <ArrowLeft className="w-4 h-4" /> Back to Funding Search
      </Link>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* ── Left 2 Columns: Main Details ── */}
        <div className="lg:col-span-2 space-y-6">
          <div className="glass p-8 space-y-6">
            <div className="flex flex-wrap items-center gap-2">
              <span className="badge badge-brand">{opp.funding_type}</span>
              <span className="badge bg-white/5 text-surface-300">{opp.funder_type}</span>
            </div>

            <h1 className="text-2xl md:text-3xl font-extrabold text-white leading-tight">
              {opp.title}
            </h1>

            <div className="flex flex-wrap items-center gap-6 text-sm text-surface-300 border-y border-white/5 py-4">
              <span className="flex items-center gap-2">
                <Building className="w-4 h-4 text-brand-400" />
                <span className="font-semibold text-white">{opp.funder_name}</span>
              </span>
              <span className="flex items-center gap-2">
                <DollarSign className="w-4 h-4 text-accent-400" />
                <span>
                  {opp.amount_min ? `$${(opp.amount_min / 1000).toFixed(0)}K` : 'Varies'} -{' '}
                  {opp.amount_max ? `$${(opp.amount_max / 1000).toFixed(0)}K` : 'Open'} {opp.currency}
                </span>
              </span>
            </div>

            {/* Description */}
            <div className="space-y-3">
              <h3 className="text-lg font-bold text-white">Program Overview</h3>
              <p className="text-surface-300 text-sm leading-relaxed whitespace-pre-line">
                {opp.description}
              </p>
            </div>

            {/* Research Domains */}
            <div className="space-y-3 pt-4 border-t border-white/5">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Tag className="w-4 h-4 text-brand-400" /> Target Research Domains
              </h3>
              <div className="flex flex-wrap gap-2">
                {opp.research_domains?.map((d) => (
                  <span key={d} className="badge bg-brand-500/20 text-brand-300 border border-brand-500/30">
                    {d}
                  </span>
                ))}
              </div>
            </div>

            {/* Keywords */}
            <div className="space-y-3">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-accent-400" /> Focus Keywords & Technologies
              </h3>
              <div className="flex flex-wrap gap-2">
                {opp.keywords?.map((k) => (
                  <span key={k} className="badge bg-white/5 text-surface-300">
                    #{k}
                  </span>
                ))}
              </div>
            </div>

            {/* Eligible Regions */}
            <div className="space-y-3">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Globe className="w-4 h-4 text-green-400" /> Eligible Countries & Regions
              </h3>
              <div className="flex flex-wrap gap-2">
                {opp.eligible_countries?.map((c) => (
                  <span key={c} className="badge bg-green-500/10 text-green-300">
                    {c}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* ── Right Column: Action Box & Sidebar ── */}
        <div className="space-y-6">
          <div className="glass p-6 space-y-6">
            <div className="space-y-2 text-center pb-4 border-b border-white/5">
              <p className="text-xs text-surface-400 uppercase tracking-wider font-semibold">Maximum Award</p>
              <p className="text-3xl font-extrabold text-accent-400">
                {opp.amount_max ? `$${(opp.amount_max / 1000).toFixed(0)}K` : 'Varies'} {opp.currency}
              </p>
            </div>

            <div className="space-y-3">
              <a
                href={opp.application_url}
                target="_blank"
                rel="noopener noreferrer"
                className="btn-primary w-full py-3 text-sm justify-center"
              >
                Apply on Official Portal <ExternalLink className="w-4 h-4 ml-1" />
              </a>

              <button
                onClick={handleToggleBookmark}
                className={clsx(
                  'btn-secondary w-full py-3 text-sm justify-center',
                  opp.is_bookmarked && 'border-brand-500 text-brand-300 bg-brand-500/10'
                )}
              >
                <Bookmark className="w-4 h-4" />
                {opp.is_bookmarked ? 'Saved to Bookmarks' : 'Bookmark Grant'}
              </button>
            </div>

            <div className="space-y-3 text-xs text-surface-300 pt-4 border-t border-white/5">
              <div className="flex items-center justify-between">
                <span className="text-surface-400">Application Deadline</span>
                <span className="font-semibold text-white">
                  {opp.deadline ? new Date(opp.deadline).toLocaleDateString() : 'Rolling Application'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-surface-400">Funder Agency</span>
                <span className="font-semibold text-white truncate max-w-[150px]">{opp.funder_name}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-surface-400">Verification Status</span>
                <span className="flex items-center gap-1 text-green-400 font-semibold">
                  <ShieldCheck className="w-3.5 h-3.5" /> Verified Listing
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
