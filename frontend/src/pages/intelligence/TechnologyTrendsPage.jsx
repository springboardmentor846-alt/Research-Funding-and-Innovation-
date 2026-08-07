import { useState, useEffect } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import {
  Search, Filter, Cpu, Layers, TrendingUp, RefreshCw,
  ChevronLeft, ChevronRight, ArrowUpDown, Building2, Zap, Compass
} from 'lucide-react'
import { technologyService } from '@/services/technologyService'
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

const MATURITY_OPTIONS = [
  'All Maturity Levels',
  'TRL 1-3 (Basic Research)',
  'TRL 4-6 (Validation & Prototype)',
  'TRL 7-9 (Commercial Deployment)',
]

export default function TechnologyTrendsPage() {
  const [searchParams] = useSearchParams()

  const [q, setQ] = useState(searchParams.get('q') || '')
  const [domain, setDomain] = useState(searchParams.get('domain') || 'All Technology Domains')
  const [maturityLevel, setMaturityLevel] = useState(searchParams.get('maturity') || 'All Maturity Levels')
  const [sortBy, setSortBy] = useState(searchParams.get('sort_by') || 'growth_desc')
  const [page, setPage] = useState(parseInt(searchParams.get('page') || '1', 10))

  const [results, setResults] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchTrends()
  }, [domain, maturityLevel, sortBy, page])

  const fetchTrends = async (overrideParams = {}) => {
    try {
      setIsLoading(true)
      const params = {
        q: q.trim() || undefined,
        domain: domain !== 'All Technology Domains' ? domain : undefined,
        maturity_level: maturityLevel !== 'All Maturity Levels' ? maturityLevel : undefined,
        sort_by: sortBy,
        page,
        page_size: 12,
        ...overrideParams,
      }

      const res = await technologyService.searchTrends(params)
      setResults(res)
    } catch (err) {
      toast.error('Failed to load technology trends.')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSearchSubmit = (e) => {
    e.preventDefault()
    setPage(1)
    fetchTrends({ page: 1 })
  }

  const handleResetFilters = () => {
    setQ('')
    setDomain('All Technology Domains')
    setMaturityLevel('All Maturity Levels')
    setSortBy('growth_desc')
    setPage(1)
    fetchTrends({
      q: undefined,
      domain: undefined,
      maturity_level: undefined,
      sort_by: 'growth_desc',
      page: 1,
    })
  }

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* ── Header ── */}
      <div>
        <div className="flex items-center gap-2 text-brand-400 font-semibold text-xs tracking-wider uppercase mb-1">
          <TrendingUp className="w-4 h-4" /> Global Technology Trends
        </div>
        <h1 className="text-2xl md:text-3xl font-extrabold text-white">Search Technology Trends & Maturity</h1>
        <p className="text-surface-400 text-sm mt-1">
          Explore 50+ technology trends categorized by Technology Readiness Level (TRL 1–9), growth velocity, and market size.
        </p>
      </div>

      {/* ── Search & Filter Controls ── */}
      <form onSubmit={handleSearchSubmit} className="glass p-6 rounded-2xl border border-white/10 space-y-4">
        {/* Keyword Search Row */}
        <div className="flex flex-col md:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="w-5 h-5 text-surface-400 absolute left-4 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Search trend name, summary, keywords, or market opportunity..."
              className="w-full bg-surface-900/80 border border-white/10 rounded-xl pl-11 pr-4 py-3 text-sm text-white placeholder-surface-500 focus:border-brand-500 focus:outline-none transition-colors"
            />
          </div>

          <button type="submit" className="btn-primary py-3 px-6 shadow-glow-brand flex items-center justify-center gap-2 text-sm">
            <Search className="w-4 h-4" />
            Search
          </button>
        </div>

        {/* Filter Controls Row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-2">
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

          {/* Maturity Level Filter */}
          <div>
            <label className="text-[11px] text-surface-400 font-medium mb-1 block">Maturity Level (TRL)</label>
            <select
              value={maturityLevel}
              onChange={(e) => { setMaturityLevel(e.target.value); setPage(1); }}
              className="w-full bg-surface-900 border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:border-brand-500 focus:outline-none"
            >
              {MATURITY_OPTIONS.map((opt) => (
                <option key={opt} value={opt}>{opt}</option>
              ))}
            </select>
          </div>

          {/* Sort By */}
          <div>
            <label className="text-[11px] text-surface-400 font-medium mb-1 block">Sort Order</label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="w-full bg-surface-900 border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:border-brand-500 focus:outline-none"
            >
              <option value="growth_desc">Highest Growth Rate (+%)</option>
              <option value="market_desc">Largest Market Size ($B)</option>
              <option value="trl_desc">Highest TRL Level (TRL 9)</option>
              <option value="trl_asc">Lowest TRL Level (TRL 1)</option>
            </select>
          </div>

          {/* Reset Filters */}
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

      {/* ── Results Header ── */}
      <div className="flex items-center justify-between text-xs text-surface-400">
        <p>
          Showing <span className="text-white font-bold">{results?.items?.length || 0}</span> of{' '}
          <span className="text-white font-bold">{results?.total || 0}</span> matching technology trends
        </p>
        <p>Page {results?.page || 1} of {results?.total_pages || 1}</p>
      </div>

      {/* ── Loading Spinner or Grid ── */}
      {isLoading ? (
        <div className="flex flex-col items-center justify-center min-h-[40vh] gap-3">
          <div className="w-10 h-10 rounded-full border-3 border-brand-500 border-t-transparent animate-spin" />
          <p className="text-surface-400 text-xs animate-pulse">Loading technology trends...</p>
        </div>
      ) : results?.items?.length === 0 ? (
        <div className="glass p-12 rounded-2xl border border-white/10 text-center space-y-3">
          <Cpu className="w-12 h-12 text-surface-500 mx-auto" />
          <h3 className="text-lg font-bold text-white">No Technology Trends Found</h3>
          <p className="text-surface-400 text-xs max-w-md mx-auto">
            No trends matched your filter criteria. Try adjusting your search query or maturity level filter.
          </p>
          <button onClick={handleResetFilters} className="btn-secondary text-xs mt-2">
            Reset Filters
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {results?.items?.map((trend) => (
            <div
              key={trend.id}
              className="glass p-5 rounded-2xl border border-white/10 hover:border-brand-500/30 transition-all flex flex-col justify-between group"
            >
              <div className="space-y-3">
                {/* TRL & Growth Badge */}
                <div className="flex items-center justify-between gap-2">
                  <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-brand-500/20 text-brand-300 border border-brand-500/30">
                    TRL-{trend.trl_level} · {trend.maturity_level}
                  </span>
                  <span className="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-2.5 py-0.5 rounded-full border border-emerald-500/20 whitespace-nowrap">
                    +{trend.growth_rate}% Growth
                  </span>
                </div>

                {/* Name */}
                <h3 className="text-base font-bold text-white group-hover:text-brand-300 transition-colors line-clamp-2">
                  {trend.name}
                </h3>

                {/* Domain */}
                <div className="text-xs text-surface-400 flex items-center gap-1.5">
                  <Layers className="w-3.5 h-3.5 text-surface-500 flex-shrink-0" />
                  <span className="truncate">{trend.technology_domain}</span>
                </div>

                {/* Summary */}
                <p className="text-xs text-surface-400 line-clamp-3 leading-relaxed">
                  {trend.summary}
                </p>

                {/* Opportunity Gap */}
                <div className="p-2.5 bg-surface-900/90 rounded-xl border border-white/5 space-y-1">
                  <span className="text-[10px] text-accent-400 font-bold uppercase tracking-wider block">Market Opportunity</span>
                  <p className="text-[11px] text-surface-300 line-clamp-2 leading-normal">
                    {trend.opportunity_description}
                  </p>
                </div>

                {/* Key Players */}
                <div className="flex flex-wrap items-center gap-1 text-[11px] text-surface-400 pt-1">
                  <span className="text-surface-500">Key Players:</span>
                  {trend.key_players?.slice(0, 3).map((player, i) => (
                    <span key={i} className="bg-surface-800 text-surface-300 px-2 py-0.5 rounded text-[10px]">
                      {player}
                    </span>
                  ))}
                </div>
              </div>

              {/* Card Footer */}
              <div className="pt-4 mt-4 border-t border-white/5 flex items-center justify-between text-xs text-surface-400">
                <span className="text-[11px]">Est. Market: <strong className="text-white">${trend.market_size_usd_b}B</strong></span>
                <span className="text-brand-400 font-medium text-[11px]">Year {trend.year}</span>
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
    </div>
  )
}
