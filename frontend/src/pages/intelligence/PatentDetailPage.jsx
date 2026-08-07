import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  ArrowLeft, Building2, User, Calendar, Layers,
  FileCheck, ShieldCheck, ExternalLink, Bookmark,
  Share2, Award, Hash, CheckCircle2, Sparkles
} from 'lucide-react'
import { patentService } from '@/services/patentService'
import toast from 'react-hot-toast'

export default function PatentDetailPage() {
  const { id } = useParams()
  const [patent, setPatent] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchPatentDetails()
  }, [id])

  const fetchPatentDetails = async () => {
    try {
      setIsLoading(true)
      const data = await patentService.getPatentDetails(id)
      setPatent(data)
    } catch (err) {
      toast.error('Failed to load patent details.')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-3">
        <div className="w-12 h-12 rounded-full border-4 border-brand-500 border-t-transparent animate-spin" />
        <p className="text-surface-400 text-sm animate-pulse">Loading Patent Details...</p>
      </div>
    )
  }

  if (!patent) {
    return (
      <div className="glass p-12 rounded-2xl border border-white/10 text-center space-y-4 max-w-xl mx-auto my-12">
        <FileCheck className="w-12 h-12 text-surface-500 mx-auto" />
        <h2 className="text-xl font-bold text-white">Patent Record Not Found</h2>
        <p className="text-surface-400 text-xs">The requested patent record could not be found or has been removed.</p>
        <Link to="/patent-intelligence/search" className="btn-secondary text-xs inline-flex items-center gap-2">
          <ArrowLeft className="w-4 h-4" /> Back to Search
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* ── Back Navigation ── */}
      <Link
        to="/patent-intelligence/search"
        className="inline-flex items-center gap-2 text-xs font-semibold text-surface-400 hover:text-white transition-colors"
      >
        <ArrowLeft className="w-4 h-4" /> Back to Patent Search
      </Link>

      {/* ── Title Header Card ── */}
      <div className="glass p-8 rounded-2xl border border-white/10 space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <span className="text-sm font-mono font-bold px-3 py-1 rounded-full bg-brand-500/20 text-brand-300 border border-brand-500/30">
              {patent.patent_number}
            </span>
            <span className={`text-xs px-3 py-1 rounded-full font-bold ${
              patent.status === 'Granted' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' :
              patent.status === 'Pending' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
              'bg-surface-800 text-surface-400'
            }`}>
              {patent.status} Patent
            </span>
          </div>

          {patent.url && (
            <a
              href={patent.url}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-secondary text-xs py-1.5 px-3 flex items-center gap-2"
            >
              Google Patents <ExternalLink className="w-3.5 h-3.5" />
            </a>
          )}
        </div>

        <h1 className="text-2xl md:text-3xl font-extrabold text-white leading-tight">
          {patent.title}
        </h1>

        {/* Core Metadata Pills */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 pt-2 border-t border-white/5 text-xs">
          <div className="flex items-center gap-3">
            <Building2 className="w-4 h-4 text-brand-400 flex-shrink-0" />
            <div>
              <p className="text-surface-500 text-[10px]">Assignee Organization</p>
              <p className="font-bold text-white truncate">{patent.assignee_organization}</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Calendar className="w-4 h-4 text-amber-400 flex-shrink-0" />
            <div>
              <p className="text-surface-500 text-[10px]">Publication Date</p>
              <p className="font-bold text-white">{patent.publication_date}</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Award className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            <div>
              <p className="text-surface-500 text-[10px]">Citations Received</p>
              <p className="font-bold text-emerald-400">{patent.citations_count} Citations</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Hash className="w-4 h-4 text-accent-400 flex-shrink-0" />
            <div>
              <p className="text-surface-500 text-[10px]">Patent Claims</p>
              <p className="font-bold text-white">{patent.claims_count} Independent Claims</p>
            </div>
          </div>
        </div>
      </div>

      {/* ── Main Details Grid ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Abstract & Classifications (2 cols) */}
        <div className="lg:col-span-2 space-y-6">
          {/* Abstract */}
          <div className="glass p-6 rounded-2xl border border-white/10 space-y-3">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <FileCheck className="w-5 h-5 text-brand-400" />
              Patent Abstract & Invention Summary
            </h2>
            <p className="text-sm text-surface-300 leading-relaxed whitespace-pre-line">
              {patent.abstract}
            </p>
          </div>

          {/* Inventors */}
          <div className="glass p-6 rounded-2xl border border-white/10 space-y-3">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <User className="w-5 h-5 text-accent-400" />
              Documented Inventors
            </h2>
            <div className="flex flex-wrap gap-2">
              {patent.inventors?.map((inv, idx) => (
                <div key={idx} className="flex items-center gap-2 bg-surface-900 border border-white/10 px-3 py-2 rounded-xl text-xs text-white">
                  <User className="w-3.5 h-3.5 text-brand-400" />
                  <span className="font-medium">{inv}</span>
                </div>
              ))}
            </div>
          </div>

          {/* IPC & CPC Classification Codes */}
          <div className="glass p-6 rounded-2xl border border-white/10 space-y-4">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Layers className="w-5 h-5 text-emerald-400" />
              Classification Codes
            </h2>

            <div className="space-y-3 text-xs">
              <div>
                <p className="text-surface-400 font-medium mb-1.5">International Patent Classification (IPC)</p>
                <div className="flex flex-wrap gap-2">
                  {patent.ipc_codes?.map((ipc, i) => (
                    <span key={i} className="font-mono bg-surface-900 text-brand-300 px-3 py-1 rounded-lg border border-brand-500/20 font-bold">
                      {ipc}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <p className="text-surface-400 font-medium mb-1.5">Cooperative Patent Classification (CPC)</p>
                <div className="flex flex-wrap gap-2">
                  {patent.cpc_codes?.map((cpc, i) => (
                    <span key={i} className="font-mono bg-surface-900 text-surface-300 px-3 py-1 rounded-lg border border-white/10">
                      {cpc}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar Info & Keywords (1 col) */}
        <div className="space-y-6">
          {/* Metadata Card */}
          <div className="glass p-6 rounded-2xl border border-white/10 space-y-4">
            <h3 className="text-base font-bold text-white pb-2 border-b border-white/5">
              Filing & Metadata
            </h3>

            <div className="space-y-3 text-xs">
              <div>
                <span className="text-surface-500 block">Technology Domain</span>
                <span className="text-white font-semibold">{patent.technology_domain}</span>
              </div>

              <div>
                <span className="text-surface-500 block">Filing Date</span>
                <span className="text-white font-medium">{patent.filing_date}</span>
              </div>

              <div>
                <span className="text-surface-500 block">Publication Year</span>
                <span className="text-white font-medium">{patent.publication_year}</span>
              </div>

              <div>
                <span className="text-surface-500 block">Data Source</span>
                <span className="text-surface-300 font-mono text-[11px] uppercase">{patent.source_api}</span>
              </div>
            </div>
          </div>

          {/* Keywords */}
          <div className="glass p-6 rounded-2xl border border-white/10 space-y-3">
            <h3 className="text-base font-bold text-white">Keywords</h3>
            <div className="flex flex-wrap gap-1.5">
              {patent.keywords?.map((kw, i) => (
                <span key={i} className="text-xs bg-surface-800 text-surface-200 px-2.5 py-1 rounded-lg border border-white/5">
                  #{kw}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
