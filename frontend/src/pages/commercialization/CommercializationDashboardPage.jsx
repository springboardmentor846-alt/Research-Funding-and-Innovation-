import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  Handshake, Building2, Rocket, Sparkles, Search,
  Bookmark, Send, ChevronRight, Layers, DollarSign,
  FileCheck, ShieldCheck, ExternalLink, UserCheck
} from 'lucide-react'
import { commercializationService } from '@/services/commercializationService'
import toast from 'react-hot-toast'

export default function CommercializationDashboardPage() {
  const [data, setData] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setIsLoading(true)
      const summary = await commercializationService.getDashboardSummary()
      setData(summary)
    } catch (err) {
      toast.error('Failed to load commercialization dashboard.')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleToggleBookmark = async (oppId) => {
    try {
      const res = await commercializationService.toggleBookmark(oppId)
      toast.success(res.message)
      fetchDashboardData()
    } catch (err) {
      toast.error('Failed to update bookmark.')
    }
  }

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <div className="w-12 h-12 rounded-full border-4 border-brand-500 border-t-transparent animate-spin" />
        <p className="text-surface-400 text-sm animate-pulse">Loading Commercialization Intelligence...</p>
      </div>
    )
  }

  const {
    statistics,
    recommended_opportunities,
    industry_partners,
    startup_programs,
    collaboration_requests,
  } = data || {}

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* ── Header ── */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 glass p-6 rounded-2xl border border-white/10">
        <div>
          <div className="flex items-center gap-2 text-emerald-400 font-semibold text-xs tracking-wider uppercase mb-1">
            <Handshake className="w-4 h-4" /> Phase 7 · Commercialization & Tech Transfer
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white">Commercialization Dashboard</h1>
          <p className="text-surface-400 text-sm mt-1">
            Connect technology innovations with industry partners, venture funds, corporate R&D labs, and startup accelerators.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to="/commercialization/opportunities"
            className="btn-secondary flex items-center gap-2 text-sm"
          >
            <Search className="w-4 h-4" />
            Explore Opportunities
          </Link>
          <Link
            to="/commercialization/partners"
            className="btn-primary flex items-center gap-2 text-sm shadow-glow-brand"
          >
            <Building2 className="w-4 h-4" />
            Industry Partners
          </Link>
        </div>
      </div>

      {/* ── Statistics Cards ── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass p-5 rounded-2xl border border-white/5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-brand-500/20 text-brand-400 flex items-center justify-center flex-shrink-0">
            <Handshake className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs text-surface-400 font-medium">Total Opportunities</p>
            <p className="text-2xl font-bold text-white mt-0.5">{statistics?.total_opportunities || 0}</p>
            <span className="text-[10px] text-surface-500">Licensing & Joint R&D</span>
          </div>
        </div>

        <div className="glass p-5 rounded-2xl border border-white/5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center flex-shrink-0">
            <Building2 className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs text-surface-400 font-medium">Active Partners</p>
            <p className="text-2xl font-bold text-emerald-400 mt-0.5">{statistics?.active_partners || 0}</p>
            <span className="text-[10px] text-emerald-500/80 font-medium">Corporate R&D Networks</span>
          </div>
        </div>

        <div className="glass p-5 rounded-2xl border border-white/5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-amber-500/20 text-amber-400 flex items-center justify-center flex-shrink-0">
            <Rocket className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs text-surface-400 font-medium">Startup Programs</p>
            <p className="text-2xl font-bold text-amber-400 mt-0.5">{statistics?.startup_programs_count || 0}</p>
            <span className="text-[10px] text-amber-500/80 font-medium">Accelerators & Funds</span>
          </div>
        </div>

        <div className="glass p-5 rounded-2xl border border-white/5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-accent-500/20 text-accent-400 flex items-center justify-center flex-shrink-0">
            <UserCheck className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs text-surface-400 font-medium">My Requests</p>
            <p className="text-2xl font-bold text-accent-300 mt-0.5">{statistics?.collaboration_requests || 0}</p>
            <span className="text-[10px] text-surface-500">Bookmarks & Inquiries</span>
          </div>
        </div>
      </div>

      {/* ── AI Recommended Commercialization Opportunities ── */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-accent-400 animate-pulse" />
            <h2 className="text-xl font-bold text-white">Recommended Opportunities</h2>
          </div>
          <Link to="/commercialization/opportunities" className="text-xs text-brand-400 hover:underline">
            View Marketplace ({statistics?.total_opportunities}) →
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {recommended_opportunities?.map((opp) => (
            <div
              key={opp.id}
              className="glass p-5 rounded-2xl border border-white/10 hover:border-brand-500/30 transition-all flex flex-col justify-between group space-y-4"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-brand-500/20 text-brand-300 border border-brand-500/30">
                    {opp.opportunity_type}
                  </span>
                  <div className="flex items-center gap-1 px-2.5 py-1 rounded-full bg-emerald-500/20 text-emerald-400 text-xs font-bold border border-emerald-500/30">
                    <Sparkles className="w-3.5 h-3.5" />
                    {opp.match_score}% Match
                  </div>
                </div>

                <Link
                  to={`/commercialization/${opp.id}`}
                  className="text-base font-bold text-white group-hover:text-brand-300 transition-colors line-clamp-2"
                >
                  {opp.title}
                </Link>

                <div className="flex items-center gap-3 text-xs text-surface-400">
                  <span className="text-surface-300 font-medium"><Building2 className="w-3.5 h-3.5 inline mr-1 text-brand-400" />{opp.organization_name}</span>
                  <span>· TRL-{opp.trl_requirement}+</span>
                </div>

                <p className="text-xs text-surface-400 line-clamp-2 leading-relaxed">{opp.summary}</p>

                <p className="text-[11px] text-accent-300/90 italic">
                  "{opp.recommendation_reason}"
                </p>
              </div>

              {/* Card Action Footer */}
              <div className="pt-4 border-t border-white/5 flex items-center justify-between text-xs">
                <span className="text-surface-400 text-[11px]">Partner: <strong className="text-white">{opp.suggested_industry_partner}</strong></span>
                
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleToggleBookmark(opp.id)}
                    className={`p-1.5 rounded-lg border transition-colors ${
                      opp.is_bookmarked ? 'bg-amber-500/20 border-amber-500/30 text-amber-400' : 'bg-surface-800 border-white/10 text-surface-400 hover:text-white'
                    }`}

                  >
                    <Bookmark className="w-4 h-4 fill-current" />
                  </button>

                  <Link
                    to={`/commercialization/${opp.id}`}
                    className="btn-primary text-xs py-1.5 px-3 flex items-center gap-1 shadow-glow-brand"
                  >
                    View Details <ChevronRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── Industry Partners & Startup Programs Grid ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Industry Partners (1 col) */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Building2 className="w-5 h-5 text-brand-400" />
              <h2 className="text-xl font-bold text-white">Featured Industry Partners</h2>
            </div>
            <Link to="/commercialization/partners" className="text-xs text-brand-400 hover:underline">
              View All Partners ({statistics?.active_partners}) →
            </Link>
          </div>

          <div className="space-y-3">
            {industry_partners?.map((partner) => (
              <div key={partner.id} className="glass p-4 rounded-xl border border-white/5 space-y-2">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-white">{partner.name}</h3>
                  <span className="text-[10px] font-semibold bg-surface-800 text-surface-300 px-2 py-0.5 rounded border border-white/5">
                    {partner.organization_type}
                  </span>
                </div>
                <p className="text-xs text-surface-400 line-clamp-2">{partner.description}</p>
                <div className="flex flex-wrap gap-1 text-[10px] text-surface-400 pt-1">
                  {partner.technology_focus?.slice(0, 3).map((tf, i) => (
                    <span key={i} className="bg-brand-500/10 text-brand-300 px-2 py-0.5 rounded">
                      {tf}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Startup Programs (1 col) */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Rocket className="w-5 h-5 text-amber-400" />
              <h2 className="text-xl font-bold text-white">Startup Accelerators & Funds</h2>
            </div>
            <Link to="/commercialization/startups" className="text-xs text-amber-400 hover:underline">
              View All Programs ({statistics?.startup_programs_count}) →
            </Link>
          </div>

          <div className="space-y-3">
            {startup_programs?.map((program) => (
              <div key={program.id} className="glass p-4 rounded-xl border border-white/5 space-y-2">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-white">{program.program_name}</h3>
                  <span className="text-xs font-bold text-amber-400 bg-amber-500/10 px-2.5 py-0.5 rounded-full border border-amber-500/20">
                    ${(program.funding_amount_usd / 1000).toFixed(0)}k Funding
                  </span>
                </div>
                <p className="text-xs text-surface-400 line-clamp-2">{program.description}</p>
                <div className="flex items-center justify-between text-[11px] text-surface-400 pt-1">
                  <span>Organizer: <strong className="text-surface-300">{program.organizer}</strong></span>
                  <span className="text-surface-500 font-mono text-[10px]">{program.duration_months} Months</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
