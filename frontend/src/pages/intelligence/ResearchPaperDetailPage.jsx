import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  BookOpen, User, Calendar, Award, ExternalLink, ArrowLeft,
  Tag, Sparkles, ShieldCheck, Layers, Globe
} from 'lucide-react'
import toast from 'react-hot-toast'
import { researchIntelligenceService } from '@/services/researchIntelligenceService'
import { clsx } from 'clsx'

export default function ResearchPaperDetailPage() {
  const { id } = useParams()
  const [paper, setPaper] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadPaper()
  }, [id])

  const loadPaper = async () => {
    try {
      setLoading(true)
      const res = await researchIntelligenceService.getPaperDetails(id)
      setPaper(res)
    } catch (err) {
      toast.error('Failed to load paper details')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="w-10 h-10 border-4 border-brand-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (!paper) {
    return (
      <div className="glass p-12 text-center space-y-4 max-w-xl mx-auto">
        <h3 className="text-xl font-bold text-white">Paper Not Found</h3>
        <p className="text-surface-400 text-sm">The research paper requested could not be located in the database.</p>
        <Link to="/research-intelligence/search" className="btn-primary text-xs">Back to Search</Link>
      </div>
    )
  }

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      {/* Back link */}
      <Link to="/research-intelligence/search" className="inline-flex items-center gap-2 text-xs font-semibold text-surface-400 hover:text-white transition-colors">
        <ArrowLeft className="w-4 h-4" /> Back to Paper Search
      </Link>

      <div className="glass p-8 space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="badge badge-brand">{paper.publication_year}</span>
            {paper.open_access && <span className="badge badge-green">Open Access</span>}
            <span className="badge bg-white/5 text-surface-300">Provider: {paper.source_api}</span>
          </div>
          <span className="flex items-center gap-1.5 text-sm font-bold text-accent-400">
            <Award className="w-4 h-4" /> {paper.citations_count} Citations ({paper.influential_citations_count} Influential)
          </span>
        </div>

        <h1 className="text-2xl md:text-3xl font-extrabold text-white leading-tight">
          {paper.title}
        </h1>

        <div className="space-y-2 border-y border-white/5 py-4 text-sm text-surface-300">
          <p className="flex items-center gap-2">
            <User className="w-4 h-4 text-brand-400 flex-shrink-0" />
            <span className="font-semibold text-white">{paper.authors?.join(', ')}</span>
          </p>
          <p className="flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-accent-400 flex-shrink-0" />
            <span>Published in <span className="font-semibold text-white">{paper.venue}</span> ({paper.publication_year})</span>
          </p>
        </div>

        {/* Abstract */}
        <div className="space-y-3">
          <h3 className="text-lg font-bold text-white">Abstract</h3>
          <p className="text-surface-300 text-sm leading-relaxed whitespace-pre-line">
            {paper.abstract}
          </p>
        </div>

        {/* Research Domains */}
        <div className="space-y-3 pt-4 border-t border-white/5">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Tag className="w-4 h-4 text-brand-400" /> Research Domains
          </h3>
          <div className="flex flex-wrap gap-2">
            {paper.research_domains?.map((d) => (
              <span key={d} className="badge bg-brand-500/20 text-brand-300 border border-brand-500/30">
                {d}
              </span>
            ))}
          </div>
        </div>

        {/* Keywords */}
        <div className="space-y-3">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-accent-400" /> Keywords & Topics
          </h3>
          <div className="flex flex-wrap gap-2">
            {paper.keywords?.map((k) => (
              <span key={k} className="badge bg-white/5 text-surface-300">
                #{k}
              </span>
            ))}
          </div>
        </div>

        {/* DOI / External link */}
        {paper.url && (
          <div className="pt-6 border-t border-white/5 flex items-center justify-between">
            <span className="text-xs text-surface-400">DOI: {paper.doi || 'Available'}</span>
            <a
              href={paper.url}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-primary text-xs"
            >
              Access Full Paper via DOI <ExternalLink className="w-3.5 h-3.5 ml-1" />
            </a>
          </div>
        )}
      </div>
    </div>
  )
}
