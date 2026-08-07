import { useState, useEffect } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import {
  Search, Filter, Building2, Layers, Handshake,
  Bookmark, Send, RefreshCw, ChevronLeft, ChevronRight,
  ArrowUpDown, CheckCircle2, X
} from 'lucide-react'
import { commercializationService } from '@/services/commercializationService'
import toast from 'react-hot-toast'

const DOMAIN_OPTIONS = [
  'All Technology Domains',
  'Artificial Intelligence & Machine Learning',
  'Quantum Computing & Information',
  'Biotechnology & Genomics',
  'Clean Energy & Storage',
  'Cybersecurity & Cryptography',
  'Robotics & Autonomous Systems',
  'Semiconductors & Microelectronics',
  'MedTech & Medical Devices',
  'Wireless Communications & 6G',
  'Autonomous Vehicles & Mobility',
]

const TYPE_OPTIONS = [
  'All Opportunity Types',
  'Technology Licensing',
  'Joint R&D',
  'Corporate Venture Capital',
  'Startup Accelerator',
  'Contract Research',
]

export default function CollaborationOpportunitiesPage() {
  const [searchParams] = useSearchParams()

  const [q, setQ] = useState(searchParams.get('q') || '')
  const [domain, setDomain] = useState(searchParams.get('domain') || 'All Technology Domains')
  const [industry, setIndustry] = useState(searchParams.get('industry') || '')
  const [organization, setOrganization] = useState(searchParams.get('organization') || '')
  const [opportunityType, setOpportunityType] = useState(searchParams.get('type') || 'All Opportunity Types')
  const [sortBy, setSortBy] = useState(searchParams.get('sort_by') || 'created_desc')
  const [page, setPage] = useState(parseInt(searchParams.get('page') || '1', 10))

  const [results, setResults] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  // Contact Modal State
  const [contactOpp, setContactOpp] = useState(null)
  const [contactMessage, setContactMessage] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    fetchOpportunities()
  }, [domain, opportunityType, sortBy, page])

  const fetchOpportunities = async (overrideParams = {}) => {
    try {
      setIsLoading(true)
      const params = {
        q: q.trim() || undefined,
        domain: domain !== 'All Technology Domains' ? domain : undefined,
        industry: industry.trim() || undefined,
        organization: organization.trim() || undefined,
        opportunity_type: opportunityType !== 'All Opportunity Types' ? opportunityType : undefined,
        sort_by: sortBy,
        page,
        page_size: 12,
        ...overrideParams,
      }

      const res = await commercializationService.searchOpportunities(params)
      setResults(res)
    } catch (err) {
      toast.error('Failed to load commercialization opportunities.')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSearchSubmit = (e) => {
    e.preventDefault()
    setPage(1)
    fetchOpportunities({ page: 1 })
  }

  const handleResetFilters = () => {
    setQ('')
    setDomain('All Technology Domains')
    setIndustry('')
    setOrganization('')
    setOpportunityType('All Opportunity Types')
    setSortBy('created_desc')
    setPage(1)
    fetchOpportunities({
      q: undefined,
      domain: undefined,
      industry: undefined,
      organization: undefined,
      opportunity_type: undefined,
      sort_by: 'created_desc',
      page: 1,
    })
  }

  const handleToggleBookmark = async (oppId) => {
    try {
      const res = await commercializationService.toggleBookmark(oppId)
      toast.success(res.message)
      fetchOpportunities()
    } catch (err) {
      toast.error('Failed to update bookmark.')
    }
  }

  const handleOpenContactModal = (opp) => {
    setContactOpp(opp)
    setContactMessage(`We are interested in discussing commercial collaboration on "${opp.title}".`)
  }

  const handleSendContactRequest = async () => {
    if (!contactOpp) return
    try {
      setIsSubmitting(true)
      await commercializationService.submitCollaborationRequest(contactOpp.id, {
        status: 'contacted',
        message: contactMessage,
      })
      toast.success(`Interest request submitted to ${contactOpp.organization_name}!`)
      setContactOpp(null)
    } catch (err) {
      toast.error('Failed to submit collaboration request.')
      console.error(err)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* ── Header ── */}
      <div>
        <div className="flex items-center gap-2 text-brand-400 font-semibold text-xs tracking-wider uppercase mb-1">
          <Handshake className="w-4 h-4" /> Commercialization Opportunities Marketplace
        </div>
        <h1 className="text-2xl md:text-3xl font-extrabold text-white">Commercialization & Joint R&D Opportunities</h1>
        <p className="text-surface-400 text-sm mt-1">
          Discover technology licensing offers, joint corporate R&D calls, contract research projects, and incubator programs.
        </p>
      </div>

      {/* ── Search & Multi-Criteria Filters ── */}
      <form onSubmit={handleSearchSubmit} className="glass p-6 rounded-2xl border border-white/10 space-y-4">
        {/* Search Row */}
        <div className="flex flex-col md:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="w-5 h-5 text-surface-400 absolute left-4 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Search opportunity title, summary, organization, or technology domain..."
              className="w-full bg-surface-900/80 border border-white/10 rounded-xl pl-11 pr-4 py-3 text-sm text-white placeholder-surface-500 focus:border-brand-500 focus:outline-none transition-colors"
            />
          </div>

          <button type="submit" className="btn-primary py-3 px-6 shadow-glow-brand flex items-center justify-center gap-2 text-sm">
            <Search className="w-4 h-4" />
            Search
          </button>
        </div>

        {/* Filter Controls Row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 pt-2">
          {/* Domain Filter */}
          <div>
            <label className="text-[11px] text-surface-400 font-medium mb-1 block">Technology Domain</label>
            <select
              value={domain}
              onChange={(e) => { setDomain(e.target.value); setPage(1); }}
              className="w-full bg-surface-900 border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:border-brand-500 focus:outline-none"
            >
              {DOMAIN_OPTIONS.map((opt) => (
                <option key={opt} value={opt}>{opt}</option>
              ))}
            </select>
          </div>

          {/* Opportunity Type */}
          <div>
            <label className="text-[11px] text-surface-400 font-medium mb-1 block">Opportunity Type</label>
            <select
              value={opportunityType}
              onChange={(e) => { setOpportunityType(e.target.value); setPage(1); }}
              className="w-full bg-surface-900 border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:border-brand-500 focus:outline-none"
            >
              {TYPE_OPTIONS.map((opt) => (
                <option key={opt} value={opt}>{opt}</option>
              ))}
            </select>
          </div>

          {/* Industry Filter */}
          <div>
            <label className="text-[11px] text-surface-400 font-medium mb-1 block">Industry Sector</label>
            <input
              type="text"
              value={industry}
              onChange={(e) => setIndustry(e.target.value)}
              onBlur={() => { setPage(1); fetchOpportunities({ page: 1 }); }}
              placeholder="e.g. AI, Biotech, EV"
              className="w-full bg-surface-900 border border-white/10 rounded-xl px-3 py-2 text-xs text-white placeholder-surface-500 focus:border-brand-500 focus:outline-none"
            />
          </div>

          {/* Organization Filter */}
          <div>
            <label className="text-[11px] text-surface-400 font-medium mb-1 block">Organization Name</label>
            <input
              type="text"
              value={organization}
              onChange={(e) => setOrganization(e.target.value)}
              onBlur={() => { setPage(1); fetchOpportunities({ page: 1 }); }}
              placeholder="e.g. Google, IBM, Pfizer"
              className="w-full bg-surface-900 border border-white/10 rounded-xl px-3 py-2 text-xs text-white placeholder-surface-500 focus:border-brand-500 focus:outline-none"
            />
          </div>

          {/* Reset Button */}
          <div className="flex items-end">
            <button
              type="button"
              onClick={handleResetFilters}
              className="w-full btn-secondary py-2 text-xs flex items-center justify-center gap-1.5"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              Reset Filters
            </button>
          </div>
        </div>
      </form>

      {/* ── Results Listing Header ── */}
      <div className="flex items-center justify-between text-xs text-surface-400">
        <p>
          Showing <span className="text-white font-bold">{results?.items?.length || 0}</span> of{' '}
          <span className="text-white font-bold">{results?.total || 0}</span> commercialization opportunities
        </p>
        <p>Page {results?.page || 1} of {results?.total_pages || 1}</p>
      </div>

      {/* ── Loading Spinner or Results Grid ── */}
      {isLoading ? (
        <div className="flex flex-col items-center justify-center min-h-[40vh] gap-3">
          <div className="w-10 h-10 rounded-full border-3 border-brand-500 border-t-transparent animate-spin" />
          <p className="text-surface-400 text-xs animate-pulse">Loading opportunities...</p>
        </div>
      ) : results?.items?.length === 0 ? (
        <div className="glass p-12 rounded-2xl border border-white/10 text-center space-y-3">
          <Handshake className="w-12 h-12 text-surface-500 mx-auto" />
          <h3 className="text-lg font-bold text-white">No Opportunities Found</h3>
          <p className="text-surface-400 text-xs max-w-md mx-auto">
            No opportunities matched your query. Try broadening your industry or technology domain filter.
          </p>
          <button onClick={handleResetFilters} className="btn-secondary text-xs mt-2">
            Reset Filters
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {results?.items?.map((opp) => (
            <div
              key={opp.id}
              className="glass p-5 rounded-2xl border border-white/10 hover:border-brand-500/30 transition-all flex flex-col justify-between group space-y-4"
            >
              <div className="space-y-3">
                {/* Header Type & TRL */}
                <div className="flex items-center justify-between gap-2">
                  <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-brand-500/20 text-brand-300 border border-brand-500/30">
                    {opp.opportunity_type}
                  </span>
                  <span className="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                    TRL-{opp.trl_requirement}+
                  </span>
                </div>

                {/* Title */}
                <Link
                  to={`/commercialization/${opp.id}`}
                  className="text-base font-bold text-white group-hover:text-brand-300 transition-colors line-clamp-2"
                >
                  {opp.title}
                </Link>

                {/* Organization & Domain */}
                <div className="space-y-1 text-xs text-surface-400">
                  <div className="flex items-center gap-1.5 text-surface-300 font-medium">
                    <Building2 className="w-3.5 h-3.5 text-brand-400 flex-shrink-0" />
                    <span className="truncate">{opp.organization_name}</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-surface-400 text-[11px]">
                    <Layers className="w-3.5 h-3.5 text-surface-500 flex-shrink-0" />
                    <span className="truncate">{opp.technology_domain}</span>
                  </div>
                </div>

                {/* Summary */}
                <p className="text-xs text-surface-400 line-clamp-3 leading-relaxed">
                  {opp.summary}
                </p>

                {/* Funding / Location */}
                <div className="flex items-center justify-between text-[11px] text-surface-400 pt-1">
                  <span>Location: <strong className="text-surface-300">{opp.location}</strong></span>
                  {opp.estimated_funding_usd && (
                    <span className="text-emerald-400 font-bold">
                      ${(opp.estimated_funding_usd / 1000000).toFixed(1)}M Grant/Funding
                    </span>
                  )}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="pt-4 border-t border-white/5 flex items-center justify-between gap-2 text-xs">
                <button
                  onClick={() => handleToggleBookmark(opp.id)}
                  className={`p-2 rounded-xl border transition-colors flex items-center gap-1 ${
                    opp.is_bookmarked ? 'bg-amber-500/20 border-amber-500/30 text-amber-400' : 'bg-surface-800 border-white/10 text-surface-400 hover:text-white'
                  }`}
                >
                  <Bookmark className="w-4 h-4 fill-current" />
                </button>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleOpenContactModal(opp)}
                    className="btn-secondary py-1.5 px-3 text-xs flex items-center gap-1"
                  >
                    <Send className="w-3.5 h-3.5" /> Express Interest
                  </button>

                  <Link
                    to={`/commercialization/${opp.id}`}
                    className="btn-primary py-1.5 px-3 text-xs flex items-center gap-1 shadow-glow-brand"
                  >
                    View Details
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ── Pagination ── */}
      {results?.total_pages > 1 && (
        <div className="flex items-center justify-center gap-2 pt-4">
          <button
            onClick={() => setPage((p) => Math.max(p - 1, 1))}
            disabled={page === 1}
            className="btn-secondary px-3 py-2 text-xs flex items-center gap-1 disabled:opacity-50"
          >
            <ChevronLeft className="w-4 h-4" /> Previous
          </button>

          <span className="text-xs text-surface-400 px-3">
            Page <strong className="text-white">{page}</strong> of <strong className="text-white">{results.total_pages}</strong>
          </span>

          <button
            onClick={() => setPage((p) => Math.min(p + 1, results.total_pages))}
            disabled={page === results.total_pages}
            className="btn-secondary px-3 py-2 text-xs flex items-center gap-1 disabled:opacity-50"
          >
            Next <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* ── Express Interest Modal ── */}
      {contactOpp && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass p-6 rounded-2xl border border-white/10 max-w-lg w-full space-y-4 animate-scale-in">
            <div className="flex items-center justify-between border-b border-white/5 pb-3">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Send className="w-4 h-4 text-brand-400" />
                Contact Partner: {contactOpp.organization_name}
              </h3>
              <button onClick={() => setContactOpp(null)} className="p-1 hover:bg-white/5 rounded-lg text-surface-400">
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="text-xs space-y-1">
              <p className="text-surface-400">Target Opportunity:</p>
              <p className="font-bold text-white">{contactOpp.title}</p>
              <p className="text-surface-500">Contact: {contactOpp.contact_person} ({contactOpp.contact_email})</p>
            </div>

            <div>
              <label className="text-xs text-surface-300 font-medium block mb-1">Collaboration Request Note</label>
              <textarea
                rows={4}
                value={contactMessage}
                onChange={(e) => setContactMessage(e.target.value)}
                className="w-full bg-surface-900 border border-white/10 rounded-xl p-3 text-xs text-white focus:border-brand-500 focus:outline-none"
              />
            </div>

            <div className="flex items-center justify-end gap-3 pt-2">
              <button onClick={() => setContactOpp(null)} className="btn-secondary py-2 px-4 text-xs">
                Cancel
              </button>
              <button
                onClick={handleSendContactRequest}
                disabled={isSubmitting}
                className="btn-primary py-2 px-4 text-xs shadow-glow-brand flex items-center gap-1.5 disabled:opacity-50"
              >
                <Send className="w-3.5 h-3.5" />
                {isSubmitting ? 'Sending Request...' : 'Send Interest Request'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
