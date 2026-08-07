import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  Search, Filter, Building2, GraduationCap, Award, BookOpen, ExternalLink,
  ChevronRight, RefreshCw, X, User
} from 'lucide-react'
import toast from 'react-hot-toast'
import { clsx } from 'clsx'
import { researchProfileService } from '@/services/researchProfileService'

const ORG_TYPES = [
  { value: '', label: 'All Organizations' },
  { value: 'university', label: 'University / Academia' },
  { value: 'research_institute', label: 'Research Institute' },
  { value: 'corporate_rd', label: 'Corporate R&D' },
  { value: 'startup', label: 'Tech Startup' },
  { value: 'government', label: 'Government' },
]

export default function ResearcherDirectoryPage() {
  const [loading, setLoading] = useState(true)
  const [researchers, setResearchers] = useState([])
  const [total, setTotal] = useState(0)

  // Filters state
  const [query, setQuery] = useState('')
  const [domainFilter, setDomainFilter] = useState('')
  const [techFilter, setTechFilter] = useState('')
  const [orgTypeFilter, setOrgTypeFilter] = useState('')
  const [minHIndex, setMinHIndex] = useState('')
  const [page, setPage] = useState(1)

  useEffect(() => {
    fetchResearchers()
  }, [domainFilter, techFilter, orgTypeFilter, page])

  const fetchResearchers = async (overrideQuery = null) => {
    try {
      setLoading(true)
      const res = await researchProfileService.searchResearchers({
        q: overrideQuery !== null ? overrideQuery : query,
        domain: domainFilter || undefined,
        tech_interest: techFilter || undefined,
        org_type: orgTypeFilter || undefined,
        min_h_index: minHIndex ? parseInt(minHIndex, 10) : undefined,
        page,
        page_size: 12,
      })
      setResearchers(res.items || [])
      setTotal(res.total || 0)
    } catch (err) {
      toast.error('Failed to search researchers.')
    } finally {
      setLoading(false)
    }
  }

  const handleSearchSubmit = (e) => {
    e.preventDefault()
    setPage(1)
    fetchResearchers()
  }

  const handleResetFilters = () => {
    setQuery('')
    setDomainFilter('')
    setTechFilter('')
    setOrgTypeFilter('')
    setMinHIndex('')
    setPage(1)
    fetchResearchers('')
  }

  return (
    <div className="max-w-7xl mx-auto space-y-8 animate-fade-in pb-12">
      {/* Top Banner */}
      <div className="glass-card rounded-2xl p-6 md:p-8 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-80 h-80 bg-accent-500/10 rounded-full blur-3xl -z-10 pointer-events-none" />

        <div className="space-y-3 max-w-3xl">
          <span className="badge badge-brand text-xs">Innovation Network</span>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">
            Researcher & Innovation Intelligence Directory
          </h1>
          <p className="text-surface-300 text-sm leading-relaxed">
            Discover leading researchers, academic labs, startup founders, and IP portfolios across emerging domains. Search by research focus, h-index, and technology interest.
          </p>

          {/* Search bar */}
          <form onSubmit={handleSearchSubmit} className="flex gap-2 pt-2">
            <div className="relative flex-1">
              <Search className="w-5 h-5 text-surface-400 absolute left-4 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search by researcher name, domain, institution, or keyword..."
                className="input pl-12 pr-4 py-3 text-base shadow-glow-brand"
              />
            </div>
            <button type="submit" className="btn-primary px-6 py-3 flex items-center gap-2 font-bold">
              Search
            </button>
          </form>
        </div>
      </div>

      {/* Main Grid + Filter Sidebar */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Filter Sidebar */}
        <div className="glass-card rounded-2xl p-6 space-y-6 h-fit">
          <div className="flex items-center justify-between border-b border-white/10 pb-3">
            <h2 className="font-bold text-white flex items-center gap-2 text-sm uppercase tracking-wider">
              <Filter className="w-4 h-4 text-brand-400" />
              Filters
            </h2>
            <button
              onClick={handleResetFilters}
              className="text-xs text-surface-400 hover:text-brand-300 flex items-center gap-1"
            >
              <RefreshCw className="w-3 h-3" /> Reset
            </button>
          </div>

          {/* Org Type Filter */}
          <div>
            <label className="label">Organization Type</label>
            <select
              value={orgTypeFilter}
              onChange={(e) => {
                setOrgTypeFilter(e.target.value)
                setPage(1)
              }}
              className="input bg-surface-900 text-sm"
            >
              {ORG_TYPES.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </div>

          {/* Domain Filter */}
          <div>
            <label className="label">Research Domain</label>
            <input
              type="text"
              value={domainFilter}
              onChange={(e) => setDomainFilter(e.target.value)}
              placeholder="e.g. Artificial Intelligence"
              className="input text-sm"
            />
          </div>

          {/* Technology Interest Filter */}
          <div>
            <label className="label">Technology Interest</label>
            <input
              type="text"
              value={techFilter}
              onChange={(e) => setTechFilter(e.target.value)}
              placeholder="e.g. CRISPR, Solid-State"
              className="input text-sm"
            />
          </div>

          {/* Min h-index Filter */}
          <div>
            <label className="label">Minimum h-index</label>
            <input
              type="number"
              min="0"
              value={minHIndex}
              onChange={(e) => setMinHIndex(e.target.value)}
              onBlur={() => {
                setPage(1)
                fetchResearchers()
              }}
              placeholder="e.g. 5"
              className="input text-sm"
            />
          </div>
        </div>

        {/* Results Area */}
        <div className="lg:col-span-3 space-y-6">
          <div className="flex items-center justify-between">
            <p className="text-surface-400 text-sm">
              Found <strong className="text-white">{total}</strong> researcher profiles
            </p>
          </div>

          {loading ? (
            <div className="flex flex-col items-center justify-center min-h-[40vh] gap-3">
              <div className="w-8 h-8 rounded-full border-4 border-brand-500 border-t-transparent animate-spin" />
              <p className="text-surface-400 text-sm">Searching directory...</p>
            </div>
          ) : researchers.length === 0 ? (
            <div className="glass-card rounded-2xl p-12 text-center space-y-3">
              <User className="w-12 h-12 text-surface-500 mx-auto" />
              <h3 className="text-lg font-bold text-white">No researchers matched your query</h3>
              <p className="text-surface-400 text-sm max-w-md mx-auto">
                Try broadening your search terms or resetting your filters.
              </p>
              <button onClick={handleResetFilters} className="btn-secondary text-xs px-4 py-2">
                Reset All Filters
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {researchers.map((r) => (
                <div
                  key={r.id}
                  className="glass-card rounded-2xl p-6 flex flex-col justify-between space-y-4 hover:border-brand-500/40 transition-all duration-300 group"
                >
                  <div className="space-y-4">
                    {/* Header */}
                    <div className="flex items-start gap-4">
                      <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-brand-600 to-accent-600 p-0.5 shadow-glow-brand flex-shrink-0">
                        {r.avatar_url ? (
                          <img
                            src={r.avatar_url}
                            alt={r.full_name || 'Researcher'}
                            className="w-full h-full object-cover rounded-[10px]"
                          />
                        ) : (
                          <div className="w-full h-full bg-surface-900 rounded-[10px] flex items-center justify-center text-white font-bold text-lg">
                            {r.full_name?.charAt(0).toUpperCase() || 'R'}
                          </div>
                        )}
                      </div>

                      <div className="min-w-0 flex-1">
                        <h3 className="text-lg font-bold text-white group-hover:text-brand-300 transition-colors truncate">
                          {r.full_name || 'Anonymous Researcher'}
                        </h3>
                        <p className="text-xs text-surface-300 truncate">
                          {r.position || 'Researcher'}
                        </p>
                        <p className="text-xs text-surface-400 truncate flex items-center gap-1 mt-0.5">
                          <Building2 className="w-3 h-3 text-brand-400" />
                          {r.organization_name || 'Unspecified Org'}
                        </p>
                      </div>
                    </div>

                    {/* Stats Pill */}
                    <div className="grid grid-cols-3 gap-2 bg-surface-900/60 p-2.5 rounded-xl border border-white/5 text-center text-xs">
                      <div>
                        <span className="text-surface-400 block text-[10px]">h-index</span>
                        <span className="font-bold text-brand-300">{r.h_index || 0}</span>
                      </div>
                      <div>
                        <span className="text-surface-400 block text-[10px]">Pubs</span>
                        <span className="font-bold text-accent-300">{r.publications.length}</span>
                      </div>
                      <div>
                        <span className="text-surface-400 block text-[10px]">Patents</span>
                        <span className="font-bold text-green-300">{r.patents.length}</span>
                      </div>
                    </div>

                    {/* Domains tags */}
                    {r.research_domains && r.research_domains.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 pt-1">
                        {r.research_domains.slice(0, 3).map((domain) => (
                          <span
                            key={domain}
                            className="px-2.5 py-1 rounded-lg bg-brand-500/10 text-brand-300 text-[11px] font-medium border border-brand-500/20"
                          >
                            {domain}
                          </span>
                        ))}
                        {r.research_domains.length > 3 && (
                          <span className="px-2 py-1 rounded-lg bg-surface-800 text-surface-400 text-[10px]">
                            +{r.research_domains.length - 3} more
                          </span>
                        )}
                      </div>
                    )}
                  </div>

                  {/* View Action */}
                  <div className="pt-3 border-t border-white/5 flex items-center justify-between">
                    <span className="text-xs text-surface-400 capitalize">
                      {r.organization_type?.replace('_', ' ') || 'Research'}
                    </span>
                    <Link
                      to={`/researchers/${r.user_id}`}
                      className="btn-secondary text-xs px-3.5 py-1.5 flex items-center gap-1 group-hover:bg-brand-600 group-hover:text-white transition-colors"
                    >
                      View Profile <ChevronRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Pagination */}
          {total > 12 && (
            <div className="flex justify-center gap-2 pt-6">
              <button
                disabled={page === 1}
                onClick={() => setPage((p) => p - 1)}
                className="btn-secondary text-xs px-4 py-2 disabled:opacity-50"
              >
                Previous
              </button>
              <span className="text-xs text-surface-400 flex items-center px-3">
                Page {page} of {Math.ceil(total / 12)}
              </span>
              <button
                disabled={page >= Math.ceil(total / 12)}
                onClick={() => setPage((p) => p + 1)}
                className="btn-secondary text-xs px-4 py-2 disabled:opacity-50"
              >
                Next
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
