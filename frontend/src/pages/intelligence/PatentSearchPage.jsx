import { useState, useEffect } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import {
  Search, Filter, Building2, User, Calendar, Layers,
  ShieldCheck, Clock, RefreshCw, ChevronLeft, ChevronRight,
  ExternalLink, FileCheck, ArrowUpDown
} from 'lucide-react'
import { patentService } from '@/services/patentService'
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

const STATUS_OPTIONS = ['All Statuses', 'Granted', 'Pending', 'Expired']
const YEAR_OPTIONS = ['All Publication Years', 2025, 2024, 2023, 2022, 2021, 2020, 2019, 2018]

export default function PatentSearchPage() {
  const [searchParams, setSearchParams] = useSearchParams()

  const [q, setQ] = useState(searchParams.get('q') || '')
  const [domain, setDomain] = useState(searchParams.get('domain') || 'All Technology Domains')
  const [inventor, setInventor] = useState(searchParams.get('inventor') || '')
  const [organization, setOrganization] = useState(searchParams.get('organization') || '')
  const [publicationYear, setPublicationYear] = useState(searchParams.get('year') || 'All Publication Years')
  const [status, setStatus] = useState(searchParams.get('status') || 'All Statuses')
  const [sortBy, setSortBy] = useState(searchParams.get('sort_by') || 'citations_desc')
  const [page, setPage] = useState(parseInt(searchParams.get('page') || '1', 10))

  const [results, setResults] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchPatents()
  }, [domain, publicationYear, status, sortBy, page])

  const fetchPatents = async (overrideParams = {}) => {
    try {
      setIsLoading(true)
      const params = {
        q: q.trim() || undefined,
        domain: domain !== 'All Technology Domains' ? domain : undefined,
        inventor: inventor.trim() || undefined,
        organization: organization.trim() || undefined,
        publication_year: publicationYear !== 'All Publication Years' ? parseInt(publicationYear, 10) : undefined,
        status: status !== 'All Statuses' ? status : undefined,
        sort_by: sortBy,
        page,
        page_size: 12,
        ...overrideParams,
      }

      const res = await patentService.searchPatents(params)
      setResults(res)
    } catch (err) {
      toast.error('Failed to search patents.')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSearchSubmit = (e) => {
    e.preventDefault()
    setPage(1)
    fetchPatents({ page: 1 })
  }

  const handleResetFilters = () => {
    setQ('')
    setDomain('All Technology Domains')
    setInventor('')
    setOrganization('')
    setPublicationYear('All Publication Years')
    setStatus('All Statuses')
    setSortBy('citations_desc')
    setPage(1)
    fetchPatents({
      q: undefined,
      domain: undefined,
      inventor: undefined,
      organization: undefined,
      publication_year: undefined,
      status: undefined,
      sort_by: 'citations_desc',
      page: 1,
    })
  }

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* ── Header ── */}
      <div>
        <div className="flex items-center gap-2 text-brand-400 font-semibold text-xs tracking-wider uppercase mb-1">
          <Search className="w-4 h-4" /> Patent Intelligence Search
        </div>
        <h1 className="text-2xl md:text-3xl font-extrabold text-white">Search Patent Records</h1>
        <p className="text-surface-400 text-sm mt-1">
          Filter through 100+ global patent records by keyword, assignee organization, inventor, domain, year, and legal status.
        </p>
      </div>

      {/* ── Search & Multi-Criteria Filters Card ── */}
      <form onSubmit={handleSearchSubmit} className="glass p-6 rounded-2xl border border-white/10 space-y-4">
        {/* Main Search Row */}
        <div className="flex flex-col md:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="w-5 h-5 text-surface-400 absolute left-4 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Search patent title, abstract, patent number, or keyword..."
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

          {/* Organization Filter */}
          <div>
            <label className="text-[11px] text-surface-400 font-medium mb-1 block">Assignee Organization</label>
            <input
              type="text"
              value={organization}
              onChange={(e) => setOrganization(e.target.value)}
              onBlur={() => { setPage(1); fetchPatents({ page: 1 }); }}
              placeholder="e.g. Google, IBM, TSMC"
              className="w-full bg-surface-900 border border-white/10 rounded-xl px-3 py-2 text-xs text-white placeholder-surface-500 focus:border-brand-500 focus:outline-none"
            />
          </div>

          {/* Inventor Filter */}
          <div>
            <label className="text-[11px] text-surface-400 font-medium mb-1 block">Inventor Name</label>
            <input
              type="text"
              value={inventor}
              onChange={(e) => setInventor(e.target.value)}
              onBlur={() => { setPage(1); fetchPatents({ page: 1 }); }}
              placeholder="e.g. Dr. Vance, Chen"
              className="w-full bg-surface-900 border border-white/10 rounded-xl px-3 py-2 text-xs text-white placeholder-surface-500 focus:border-brand-500 focus:outline-none"
            />
          </div>

          {/* Status Filter */}
          <div>
            <label className="text-[11px] text-surface-400 font-medium mb-1 block">Legal Status</label>
            <select
              value={status}
              onChange={(e) => { setStatus(e.target.value); setPage(1); }}
              className="w-full bg-surface-900 border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:border-brand-500 focus:outline-none"
            >
              {STATUS_OPTIONS.map((opt) => (
                <option key={opt} value={opt}>{opt}</option>
              ))}
            </select>
          </div>

          {/* Publication Year Filter */}
          <div>
            <label className="text-[11px] text-surface-400 font-medium mb-1 block">Publication Year</label>
            <select
              value={publicationYear}
              onChange={(e) => { setPublicationYear(e.target.value); setPage(1); }}
              className="w-full bg-surface-900 border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:border-brand-500 focus:outline-none"
            >
              {YEAR_OPTIONS.map((opt) => (
                <option key={opt} value={opt}>{opt}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Bottom Sorting & Reset Row */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-white/5 text-xs text-surface-400">
          <div className="flex items-center gap-2">
            <ArrowUpDown className="w-3.5 h-3.5 text-brand-400" />
            <span>Sort by:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="bg-surface-900 border border-white/10 rounded-lg px-2.5 py-1 text-xs text-white focus:outline-none"
            >
              <option value="citations_desc">Highest Citations</option>
              <option value="year_desc">Newest Publication Year</option>
              <option value="year_asc">Oldest Publication Year</option>
              <option value="claims_desc">Most Patent Claims</option>
            </select>
          </div>

          <button
            type="button"
            onClick={handleResetFilters}
            className="text-surface-400 hover:text-white flex items-center gap-1.5 transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Reset All Filters
          </button>
        </div>
      </form>

      {/* ── Results Listing Header ── */}
      <div className="flex items-center justify-between text-xs text-surface-400">
        <p>
          Showing <span className="text-white font-bold">{results?.items?.length || 0}</span> of{' '}
          <span className="text-white font-bold">{results?.total || 0}</span> matching patent records
        </p>
        <p>Page {results?.page || 1} of {results?.total_pages || 1}</p>
      </div>

      {/* ── Loading Spinner or Results Grid ── */}
      {isLoading ? (
        <div className="flex flex-col items-center justify-center min-h-[40vh] gap-3">
          <div className="w-10 h-10 rounded-full border-3 border-brand-500 border-t-transparent animate-spin" />
          <p className="text-surface-400 text-xs animate-pulse">Searching patent records...</p>
        </div>
      ) : results?.items?.length === 0 ? (
        <div className="glass p-12 rounded-2xl border border-white/10 text-center space-y-3">
          <FileCheck className="w-12 h-12 text-surface-500 mx-auto" />
          <h3 className="text-lg font-bold text-white">No Patent Records Found</h3>
          <p className="text-surface-400 text-xs max-w-md mx-auto">
            No patents matched your filter criteria. Try broadening your keywords or resetting filters.
          </p>
          <button onClick={handleResetFilters} className="btn-secondary text-xs mt-2">
            Reset Filters
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {results?.items?.map((patent) => (
            <div
              key={patent.id}
              className="glass p-5 rounded-2xl border border-white/10 hover:border-brand-500/30 transition-all flex flex-col justify-between group"
            >
              <div className="space-y-3">
                {/* Number & Status */}
                <div className="flex items-center justify-between gap-2">
                  <span className="text-xs font-mono font-bold text-brand-300 px-2.5 py-1 rounded-full bg-brand-500/10 border border-brand-500/20">
                    {patent.patent_number}
                  </span>
                  <span className={`text-[10px] px-2.5 py-0.5 rounded-full font-semibold ${
                    patent.status === 'Granted' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' :
                    patent.status === 'Pending' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                    'bg-surface-800 text-surface-400'
                  }`}>
                    {patent.status}
                  </span>
                </div>

                {/* Title */}
                <Link
                  to={`/patent-intelligence/${patent.id}`}
                  className="text-base font-bold text-white group-hover:text-brand-300 transition-colors line-clamp-2"
                >
                  {patent.title}
                </Link>

                {/* Assignee & Domain */}
                <div className="space-y-1 text-xs text-surface-400">
                  <div className="flex items-center gap-1.5 text-surface-300 font-medium">
                    <Building2 className="w-3.5 h-3.5 text-brand-400 flex-shrink-0" />
                    <span className="truncate">{patent.assignee_organization}</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-surface-400 text-[11px]">
                    <Layers className="w-3.5 h-3.5 text-surface-500 flex-shrink-0" />
                    <span className="truncate">{patent.technology_domain}</span>
                  </div>
                </div>

                {/* Abstract */}
                <p className="text-xs text-surface-400 line-clamp-3 leading-relaxed">
                  {patent.abstract}
                </p>

                {/* IPC Classification Badges */}
                <div className="flex flex-wrap gap-1">
                  {patent.ipc_codes?.slice(0, 3).map((ipc, i) => (
                    <span key={i} className="text-[10px] font-mono px-2 py-0.5 rounded bg-surface-900 text-surface-300 border border-white/5">
                      {ipc}
                    </span>
                  ))}
                </div>
              </div>

              {/* Card Footer */}
              <div className="pt-4 mt-4 border-t border-white/5 flex items-center justify-between text-xs text-surface-400">
                <span className="text-[11px]">Citations: <strong className="text-white">{patent.citations_count}</strong></span>
                <Link
                  to={`/patent-intelligence/${patent.id}`}
                  className="text-brand-400 hover:text-brand-300 font-semibold flex items-center gap-1"
                >
                  View Details →
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ── Pagination Controls ── */}
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
    </div>
  )
}
