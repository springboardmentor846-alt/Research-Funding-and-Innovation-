import { useState, useEffect } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import {
  Search, Filter, Bookmark, Building, DollarSign,
  Calendar, Globe, ChevronLeft, ChevronRight, Coins
} from 'lucide-react'
import toast from 'react-hot-toast'
import { fundingService } from '@/services/fundingService'
import { clsx } from 'clsx'

const DOMAIN_OPTIONS = [
  'All',
  'Artificial Intelligence',
  'Quantum Computing',
  'Biotechnology',
  'Clean Energy',
  'Medicine',
  'Robotics',
  'Materials Science',
  'Environmental Science',
  'Computer Science',
]

const TYPE_OPTIONS = ['All', 'Grant', 'Contract', 'Fellowship', 'Equity']
const COUNTRY_OPTIONS = ['All', 'United States', 'European Union', 'United Kingdom', 'Global']

export default function FundingSearchPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState({ items: [], total: 0, page: 1, total_pages: 1 })

  // Filters state
  const [q, setQ] = useState(searchParams.get('q') || '')
  const [domain, setDomain] = useState(searchParams.get('domain') || 'All')
  const [fundingType, setFundingType] = useState(searchParams.get('funding_type') || 'All')
  const [country, setCountry] = useState(searchParams.get('country') || 'All')
  const [sortBy, setSortBy] = useState(searchParams.get('sort_by') || 'deadline_asc')
  const [page, setPage] = useState(parseInt(searchParams.get('page') || '1', 10))

  useEffect(() => {
    fetchResults()
  }, [domain, fundingType, country, sortBy, page])

  const fetchResults = async () => {
    try {
      setLoading(true)
      const res = await fundingService.searchOpportunities({
        q,
        domain: domain !== 'All' ? domain : undefined,
        funding_type: fundingType !== 'All' ? fundingType : undefined,
        country: country !== 'All' ? country : undefined,
        sort_by: sortBy,
        page,
        page_size: 12,
      })
      setData(res)
    } catch (err) {
      toast.error('Failed to search funding opportunities')
    } finally {
      setLoading(false)
    }
  }

  const handleSearchSubmit = (e) => {
    e.preventDefault()
    setPage(1)
    fetchResults()
  }

  const handleToggleBookmark = async (oppId) => {
    try {
      const res = await fundingService.toggleBookmark(oppId)
      toast.success(res.message)
      setData((prev) => ({
        ...prev,
        items: prev.items.map((item) =>
          item.id === oppId ? { ...item, is_bookmarked: res.bookmarked } : item
        ),
      }))
    } catch (err) {
      toast.error('Failed to update bookmark')
    }
  }

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* ── Header ── */}
      <div>
        <h1 className="text-2xl md:text-3xl font-extrabold text-white">
          Funding Discovery & Search Engine
        </h1>
        <p className="text-surface-400 text-sm mt-1">
          Explore and filter 50+ verified research grants, contracts, and investment cohorts worldwide.
        </p>
      </div>

      {/* ── Search & Filter Controls ── */}
      <div className="glass p-6 space-y-6">
        <form onSubmit={handleSearchSubmit} className="flex flex-col md:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="w-5 h-5 absolute left-3.5 top-1/2 -translate-y-1/2 text-surface-400" />
            <input
              type="text"
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Search by keywords, title, or agency name (e.g. NSF, CRISPR, Quantum)..."
              className="input-field pl-11 py-3 text-sm"
            />
          </div>
          <button type="submit" className="btn-primary py-3 px-6 text-sm">
            Search Grants
          </button>
        </form>

        {/* Filter selectors */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-2 border-t border-white/5">
          <div>
            <label className="text-xs font-semibold text-surface-400 mb-1.5 block">Research Domain</label>
            <select
              value={domain}
              onChange={(e) => { setDomain(e.target.value); setPage(1); }}
              className="input-field text-xs py-2"
            >
              {DOMAIN_OPTIONS.map((d) => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-xs font-semibold text-surface-400 mb-1.5 block">Funding Type</label>
            <select
              value={fundingType}
              onChange={(e) => { setFundingType(e.target.value); setPage(1); }}
              className="input-field text-xs py-2"
            >
              {TYPE_OPTIONS.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-xs font-semibold text-surface-400 mb-1.5 block">Eligible Region</label>
            <select
              value={country}
              onChange={(e) => { setCountry(e.target.value); setPage(1); }}
              className="input-field text-xs py-2"
            >
              {COUNTRY_OPTIONS.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-xs font-semibold text-surface-400 mb-1.5 block">Sort By</label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="input-field text-xs py-2"
            >
              <option value="deadline_asc">Deadline (Soonest First)</option>
              <option value="deadline_desc">Deadline (Furthest First)</option>
              <option value="amount_desc">Funding Amount (Highest)</option>
              <option value="created_desc">Recently Added</option>
            </select>
          </div>
        </div>
      </div>

      {/* ── Results Grid ── */}
      {loading ? (
        <div className="flex items-center justify-center min-h-[300px]">
          <div className="w-10 h-10 border-4 border-brand-500 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : data.items.length === 0 ? (
        <div className="glass p-12 text-center space-y-4">
          <Coins className="w-12 h-12 text-surface-500 mx-auto" />
          <h3 className="text-lg font-bold text-white">No funding opportunities found</h3>
          <p className="text-surface-400 text-sm max-w-md mx-auto">
            Try adjusting your search terms or clearing region/domain filters.
          </p>
          <button
            onClick={() => {
              setQ(''); setDomain('All'); setFundingType('All'); setCountry('All'); setPage(1);
            }}
            className="btn-secondary text-xs"
          >
            Reset All Filters
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="flex items-center justify-between text-xs text-surface-400">
            <span>Showing {data.items.length} of {data.total} funding opportunities</span>
            <span>Page {data.page} of {data.total_pages}</span>
          </div>

          <div className="grid md:grid-cols-3 gap-5">
            {data.items.map((opp) => (
              <div key={opp.id} className="glass p-5 flex flex-col justify-between hover:border-brand-500/40 transition-all">
                <div className="space-y-3">
                  <div className="flex items-start justify-between gap-3">
                    <span className="badge badge-brand text-xs">{opp.funding_type}</span>
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

                  <div className="flex items-center gap-3 text-xs text-surface-400">
                    <span className="flex items-center gap-1">
                      <Building className="w-3.5 h-3.5 text-surface-500" /> {opp.funder_name}
                    </span>
                  </div>

                  <div className="flex items-center gap-3 text-xs font-semibold text-accent-400">
                    <DollarSign className="w-4 h-4" />
                    {opp.amount_max ? `$${(opp.amount_max / 1000).toFixed(0)}K ${opp.currency}` : 'Varies'}
                  </div>

                  <p className="text-xs text-surface-300 line-clamp-3">{opp.description}</p>

                  <div className="flex flex-wrap gap-1">
                    {opp.research_domains?.slice(0, 2).map((d) => (
                      <span key={d} className="badge bg-white/5 text-surface-300 text-[10px]">
                        {d}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-white/5 flex items-center justify-between text-xs text-surface-400">
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3.5 h-3.5" />
                    {opp.deadline ? new Date(opp.deadline).toLocaleDateString() : 'Rolling'}
                  </span>
                  <Link to={`/funding/${opp.id}`} className="text-brand-400 font-semibold hover:underline">
                    View Details →
                  </Link>
                </div>
              </div>
            ))}
          </div>

          {/* Pagination Controls */}
          {data.total_pages > 1 && (
            <div className="flex items-center justify-center gap-3 pt-4">
              <button
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                className="btn-secondary text-xs disabled:opacity-40"
              >
                <ChevronLeft className="w-4 h-4" /> Previous
              </button>
              <span className="text-xs text-surface-400">
                Page {page} of {data.total_pages}
              </span>
              <button
                disabled={page >= data.total_pages}
                onClick={() => setPage((p) => Math.min(data.total_pages, p + 1))}
                className="btn-secondary text-xs disabled:opacity-40"
              >
                Next <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
