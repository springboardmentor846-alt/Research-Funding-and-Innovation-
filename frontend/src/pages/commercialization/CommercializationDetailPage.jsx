import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  ArrowLeft, Building2, Layers, Handshake, Bookmark,
  Send, Calendar, MapPin, Mail, User, DollarSign,
  ShieldCheck, FileCheck, CheckCircle2, X, Sparkles
} from 'lucide-react'
import { commercializationService } from '@/services/commercializationService'
import toast from 'react-hot-toast'

export default function CommercializationDetailPage() {
  const { id } = useParams()
  const [opp, setOpp] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  // Contact Modal State
  const [showModal, setShowModal] = useState(false)
  const [message, setMessage] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    fetchOpportunityDetails()
  }, [id])

  const fetchOpportunityDetails = async () => {
    try {
      setIsLoading(true)
      const data = await commercializationService.getOpportunityDetails(id)
      setOpp(data)
    } catch (err) {
      toast.error('Failed to load opportunity details.')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleToggleBookmark = async () => {
    try {
      const res = await commercializationService.toggleBookmark(id)
      toast.success(res.message)
      setOpp((prev) => ({ ...prev, is_bookmarked: res.is_bookmarked }))
    } catch (err) {
      toast.error('Failed to update bookmark.')
    }
  }

  const handleSendRequest = async () => {
    try {
      setIsSubmitting(true)
      await commercializationService.submitCollaborationRequest(id, {
        status: 'contacted',
        message,
      })
      toast.success(`Interest request sent to ${opp.organization_name}!`)
      setShowModal(false)
    } catch (err) {
      toast.error('Failed to submit collaboration request.')
      console.error(err)
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-3">
        <div className="w-12 h-12 rounded-full border-4 border-brand-500 border-t-transparent animate-spin" />
        <p className="text-surface-400 text-sm animate-pulse">Loading Opportunity Details...</p>
      </div>
    )
  }

  if (!opp) {
    return (
      <div className="glass p-12 rounded-2xl border border-white/10 text-center space-y-4 max-w-xl mx-auto my-12">
        <Handshake className="w-12 h-12 text-surface-500 mx-auto" />
        <h2 className="text-xl font-bold text-white">Opportunity Not Found</h2>
        <p className="text-surface-400 text-xs">The requested commercialization opportunity could not be found.</p>
        <Link to="/commercialization/opportunities" className="btn-secondary text-xs inline-flex items-center gap-2">
          <ArrowLeft className="w-4 h-4" /> Back to Marketplace
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* ── Back Navigation ── */}
      <Link
        to="/commercialization/opportunities"
        className="inline-flex items-center gap-2 text-xs font-semibold text-surface-400 hover:text-white transition-colors"
      >
        <ArrowLeft className="w-4 h-4" /> Back to Commercialization Marketplace
      </Link>

      {/* ── Title Banner Card ── */}
      <div className="glass p-8 rounded-2xl border border-white/10 space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <span className="text-xs font-bold px-3 py-1 rounded-full bg-brand-500/20 text-brand-300 border border-brand-500/30">
              {opp.opportunity_type}
            </span>
            <span className="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20">
              TRL-{opp.trl_requirement}+ Requirement
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleToggleBookmark}
              className={`p-2 rounded-xl border transition-colors flex items-center gap-1 text-xs ${
                opp.is_bookmarked ? 'bg-amber-500/20 border-amber-500/30 text-amber-400' : 'bg-surface-800 border-white/10 text-surface-400 hover:text-white'
              }`}
            >
              <Bookmark className="w-4 h-4 fill-current" />
              {opp.is_bookmarked ? 'Bookmarked' : 'Bookmark'}
            </button>

            <button
              onClick={() => {
                setMessage(`We are interested in discussing commercial collaboration on "${opp.title}".`)
                setShowModal(true)
              }}
              className="btn-primary text-xs py-2 px-4 shadow-glow-brand flex items-center gap-1.5"
            >
              <Send className="w-4 h-4" /> Express Interest
            </button>
          </div>
        </div>

        <h1 className="text-2xl md:text-3xl font-extrabold text-white leading-tight">
          {opp.title}
        </h1>

        {/* Key Metadata Pills */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 pt-2 border-t border-white/5 text-xs">
          <div className="flex items-center gap-3">
            <Building2 className="w-4 h-4 text-brand-400 flex-shrink-0" />
            <div>
              <p className="text-surface-500 text-[10px]">Organization</p>
              <p className="font-bold text-white truncate">{opp.organization_name}</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Layers className="w-4 h-4 text-accent-400 flex-shrink-0" />
            <div>
              <p className="text-surface-500 text-[10px]">Technology Domain</p>
              <p className="font-bold text-white truncate">{opp.technology_domain}</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <MapPin className="w-4 h-4 text-amber-400 flex-shrink-0" />
            <div>
              <p className="text-surface-500 text-[10px]">Location</p>
              <p className="font-bold text-white">{opp.location}</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Calendar className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            <div>
              <p className="text-surface-500 text-[10px]">Application Deadline</p>
              <p className="font-bold text-white">{opp.deadline || 'Rolling Basis'}</p>
            </div>
          </div>
        </div>
      </div>

      {/* ── Main Details Grid ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Description & Matching Techs (2 cols) */}
        <div className="lg:col-span-2 space-y-6">
          {/* Summary & Description */}
          <div className="glass p-6 rounded-2xl border border-white/10 space-y-4">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <FileCheck className="w-5 h-5 text-brand-400" />
              Opportunity Summary & Scope
            </h2>
            <p className="text-sm font-medium text-brand-200 leading-relaxed">
              {opp.summary}
            </p>
            <div className="pt-3 border-t border-white/5 text-xs text-surface-300 leading-relaxed whitespace-pre-line">
              {opp.detailed_description}
            </div>
          </div>

          {/* Matching Technologies & Keywords */}
          <div className="glass p-6 rounded-2xl border border-white/10 space-y-4">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-accent-400" />
              Target Technologies & Key Terms
            </h2>

            <div className="space-y-3 text-xs">
              <div>
                <p className="text-surface-400 font-medium mb-1.5">Target Matching Technologies</p>
                <div className="flex flex-wrap gap-2">
                  {opp.matching_technologies?.map((tech, i) => (
                    <span key={i} className="bg-brand-500/10 text-brand-300 px-3 py-1 rounded-lg border border-brand-500/20 font-semibold">
                      ✓ {tech}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <p className="text-surface-400 font-medium mb-1.5">Key Domain Keywords</p>
                <div className="flex flex-wrap gap-1.5">
                  {opp.key_keywords?.map((kw, i) => (
                    <span key={i} className="bg-surface-900 text-surface-300 px-2.5 py-1 rounded-md border border-white/5">
                      #{kw}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar Contact Info & Funding (1 col) */}
        <div className="space-y-6">
          {/* Partner Contact Card */}
          <div className="glass p-6 rounded-2xl border border-white/10 space-y-4">
            <h3 className="text-base font-bold text-white pb-2 border-b border-white/5">
              Contact & Licensing Lead
            </h3>

            <div className="space-y-3 text-xs">
              <div className="flex items-center gap-3">
                <User className="w-4 h-4 text-brand-400" />
                <div>
                  <span className="text-surface-500 block text-[10px]">Contact Person</span>
                  <span className="font-bold text-white">{opp.contact_person}</span>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <Mail className="w-4 h-4 text-accent-400" />
                <div>
                  <span className="text-surface-500 block text-[10px]">Email Address</span>
                  <a href={`mailto:${opp.contact_email}`} className="font-semibold text-brand-300 hover:underline">
                    {opp.contact_email}
                  </a>
                </div>
              </div>

              {opp.estimated_funding_usd && (
                <div className="pt-2 border-t border-white/5">
                  <span className="text-surface-500 block text-[10px]">Estimated Funding Support</span>
                  <span className="text-lg font-bold text-emerald-400">
                    ${(opp.estimated_funding_usd / 1000000).toFixed(1)} Million USD
                  </span>
                </div>
              )}
            </div>

            <button
              onClick={() => {
                setMessage(`We are interested in discussing commercial collaboration on "${opp.title}".`)
                setShowModal(true)
              }}
              className="w-full btn-primary text-xs py-2.5 shadow-glow-brand flex items-center justify-center gap-2 mt-2"
            >
              <Send className="w-4 h-4" /> Express Interest Request
            </button>
          </div>
        </div>
      </div>

      {/* ── Express Interest Modal ── */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass p-6 rounded-2xl border border-white/10 max-w-lg w-full space-y-4 animate-scale-in">
            <div className="flex items-center justify-between border-b border-white/5 pb-3">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Send className="w-4 h-4 text-brand-400" />
                Contact Lead: {opp.organization_name}
              </h3>
              <button onClick={() => setShowModal(false)} className="p-1 hover:bg-white/5 rounded-lg text-surface-400">
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="text-xs space-y-1">
              <p className="text-surface-400">Target Opportunity:</p>
              <p className="font-bold text-white">{opp.title}</p>
              <p className="text-surface-500">Contact: {opp.contact_person} ({opp.contact_email})</p>
            </div>

            <div>
              <label className="text-xs text-surface-300 font-medium block mb-1">Collaboration Request Message</label>
              <textarea
                rows={4}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                className="w-full bg-surface-900 border border-white/10 rounded-xl p-3 text-xs text-white focus:border-brand-500 focus:outline-none"
              />
            </div>

            <div className="flex items-center justify-end gap-3 pt-2">
              <button onClick={() => setShowModal(false)} className="btn-secondary py-2 px-4 text-xs">
                Cancel
              </button>
              <button
                onClick={handleSendRequest}
                disabled={isSubmitting}
                className="btn-primary py-2 px-4 text-xs shadow-glow-brand flex items-center gap-1.5 disabled:opacity-50"
              >
                <Send className="w-3.5 h-3.5" />
                {isSubmitting ? 'Sending Request...' : 'Send Request'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
