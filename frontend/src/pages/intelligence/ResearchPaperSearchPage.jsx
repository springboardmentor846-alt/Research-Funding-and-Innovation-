import { useState, useEffect } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import {
  Search, BookOpen, User, Calendar, Award, ExternalLink,
  ChevronLeft, ChevronRight, Filter, Layers
} from 'lucide-react'
import toast from 'react-hot-toast'
import { researchIntelligenceService } from '@/services/researchIntelligenceService'
import { clsx } from 'clsx'

const DOMAIN_OPTIONS = [
  'All',
  'Quantum Computing',
  'Artificial Intelligence',
  'Biotechnology',
  'Clean Energy',
  'Computer Science',
  'Medicine',
  'Robotics',
  'Materials Science',
  'Environmental Science',
  'Cybersecurity',
]

export default function ResearchPaperSearchPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState({ items: [], total: 0, page: 1, total_pages: 1 })

  // Filters state
  const [q, setQ] = useState(searchParams.get('q') || '')
  const [domain, setDomain] = useState(searchParams.get('domain') || 'All')
  const [author, setAuthor] = useState(searchParams.get('author') || '')
  const [yearMin, setYearMin] = useState(searchParams.get('year_min') || '')
  const [sortBy, setSortBy] = useState(searchParams.get('sort_by') || 'citations_desc')
  const [page, setPage] = useState(parseInt(searchParams.get('page') || '1', 10))

  useEffect(() => {
    fetchResults()
  }, [domain, sortBy, page])

  const fetchResults = async () => {
    try {
      setLoading(true)
      const res = await researchIntelligenceService.searchPapers({
        q,
        domain: domain !== 'All' ? domain : undefined,
        author: author || undefined,
        year_min: yearMin ? parseInt(yearMin, 10) : undefined,
        sort_by: sortBy,
        page,
        page_size: 12,
      })
      setData(res)
    } catch (err) {
      toast.error('Failed to search research papers')
    } finally {
      setLoading(false)
    }
  }

  const handleSearchSubmit = (e) => {
    e.preventDefault()
    setPage(1)
    fetchResults()
  }

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* ── Header ── */}
      <div>
        <h1 className="text-2xl md:text-3xl font-extrabold text-white">
          Scientific Literature Search Engine
        </h1>
        <p className="text-surface-400 text-sm mt-1">
          Search over 100+ peer-reviewed papers across Quantum AI, Clean Energy, Genomics, and Robotics.
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
              placeholder="Search title, abstract, or venue (e.g. Surface Codes, CRISPR, Diffusion)..."
              className="input-field pl-11 py-3 text-sm"
            />
          </div>
          <button type="submit" className="btn-primary py-3 px-6 text-sm">
            Search Papers
          </button>
        </form>

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
            <label className="text-xs font-semibold text-surface-400 mb-1.5 block">Author Name</label>
            <input
              type="text"
              value={author}
              onChange={(e) => setAuthor(e.target.value)}
              onBlur={() => { setPage(1); fetchResults(); }}
              placeholder="e.g. Sarah Smith"
              className="input-field text-xs py-2"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-surface-400 mb-1.5 block">Min Year</label>
            <input
              type="number"
              value={yearMin}
              onChange={(e) => setYearMin(e.target.value)}
              onBlur={() => { setPage(1); fetchResults(); }}
              placeholder="e.g. 2022"
              className="input-field text-xs py-2"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-surface-400 mb-1.5 block">Sort By</label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="input-field text-xs py-2"
            >
              <option value="citations_desc">Most Cited</option>
              <option value="year_desc">Newest First</option>
              <option value="year_asc">Oldest First</option>
              <option value="created_desc">Recently Indexed</option>
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
          <BookOpen className="w-12 h-12 text-surface-500 mx-auto" />
          <h3 className="text-lg font-bold text-white">No papers found</h3>
          <p className="text-surface-400 text-sm max-w-md mx-auto">
            Try broadening your search keywords or clearing domain/author filters.
          </p>
          <button
            onClick={() => {
              setQ(''); setDomain('All'); setAuthor(''); setYearMin(''); setPage(1);
            }}
            className="btn-secondary text-xs"
          >
            Reset Filters
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="flex items-center justify-between text-xs text-surface-400">
            <span>Showing {data.items.length} of {data.total} research papers</span>
            <span>Page {data.page} of {data.total_pages}</span>
          </div>

          <div className="grid md:grid-cols-3 gap-5">
            {data.items.map((paper) => (
              <div key={paper.id} className="glass p-5 flex flex-col justify-between hover:border-brand-500/40 transition-all">
                <div className="space-y-3">
                  <div className="flex items-center justify-between text-xs text-surface-400">
                    <span className="flex items-center gap-1 font-semibold text-accent-400">
                      <Award className="w-3.5 h-3.5" /> {paper.citations_count} citations
                    </span>
                    <span className="badge bg-white/5 text-surface-300 text-[10px]">
                      {paper.publication_year}
                    </span>
                  </div>

                  <Link to={`/research-intelligence/paper/${paper.id}`} className="block group">
                    <h3 className="text-base font-bold text-white group-hover:text-brand-300 transition-colors line-clamp-2">
                      {paper.title}
                    </h3>
                  </Link>

                  <p className="text-xs text-surface-400 truncate">
                    <User className="w-3 h-3 inline mr-1 text-surface-500" />
                    {paper.authors?.join(', ')}
                  </p>

                  <p className="text-xs font-semibold text-brand-300 truncate">{paper.venue}</p>

                  <p className="text-xs text-surface-300 line-clamp-3">{paper.abstract}</p>

                  <div className="flex flex-wrap gap-1">
                    {paper.research_domains?.slice(0, 2).map((d) => (
                      <span key={d} className="badge bg-brand-500/10 text-brand-300 text-[10px]">
                        {d}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-white/5 flex items-center justify-between text-xs">
                  <span className="text-surface-500 text-[11px]">Provider: {paper.source_api}</span>
                  <Link to={`/research-intelligence/paper/${paper.id}`} className="text-brand-400 font-semibold hover:underline">
                    View Details →
                  </Link>
                </div>
              </div>
            ))}
          </div>

          {/* Pagination */}
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
