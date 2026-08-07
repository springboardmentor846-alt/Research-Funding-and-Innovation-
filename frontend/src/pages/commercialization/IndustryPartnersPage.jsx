import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  Building2, Search, ExternalLink, Mail, MapPin,
  Layers, Handshake, Filter, RefreshCw
} from 'lucide-react'
import { commercializationService } from '@/services/commercializationService'
import toast from 'react-hot-toast'

const INDUSTRY_OPTIONS = [
  'All Industries',
  'Artificial Intelligence & Software',
  'Quantum Computing & Information',
  'Biotechnology & Genomics',
  'Clean Energy & Storage',
  'Cybersecurity & Defense',
  'Robotics & Autonomous Systems',
  'Semiconductors & Microelectronics',
  'MedTech & Healthcare',
  'Wireless Communications & 6G',
  'Autonomous Mobility',
]

export default function IndustryPartnersPage() {
  const [q, setQ] = useState('')
  const [industry, setIndustry] = useState('All Industries')
  const [partners, setPartners] = useState([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchPartners()
  }, [industry])

  const fetchPartners = async (overrideParams = {}) => {
    try {
      setIsLoading(true)
      const params = {
        q: q.trim() || undefined,
        industry: industry !== 'All Industries' ? industry : undefined,
        ...overrideParams,
      }
      const data = await commercializationService.getIndustryPartners(params)
      setPartners(data)
    } catch (err) {
      toast.error('Failed to load industry partners.')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSearchSubmit = (e) => {
    e.preventDefault()
    fetchPartners()
  }

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* ── Header ── */}
      <div>
        <div className="flex items-center gap-2 text-brand-400 font-semibold text-xs tracking-wider uppercase mb-1">
          <Building2 className="w-4 h-4" /> Corporate R&D Partner Directory
        </div>
        <h1 className="text-2xl md:text-3xl font-extrabold text-white">Industry R&D Partners & Buyers</h1>
        <p className="text-surface-400 text-sm mt-1">
          Connect with multinational corporate R&D labs, technology buyers, and venture arms seeking academic IP and startup licensing.
        </p>
      </div>

      {/* ── Search & Filter ── */}
      <form onSubmit={handleSearchSubmit} className="glass p-5 rounded-2xl border border-white/10 flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-surface-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search partner name, technology focus, or location..."
            className="w-full bg-surface-900 border border-white/10 rounded-xl pl-10 pr-4 py-2.5 text-xs text-white placeholder-surface-500 focus:border-brand-500 focus:outline-none"
          />
        </div>

        <select
          value={industry}
          onChange={(e) => setIndustry(e.target.value)}
          className="bg-surface-900 border border-white/10 rounded-xl px-3 py-2.5 text-xs text-white focus:border-brand-500 focus:outline-none min-w-[200px]"
        >
          {INDUSTRY_OPTIONS.map((opt) => (
            <option key={opt} value={opt}>{opt}</option>
          ))}
        </select>

        <button type="submit" className="btn-primary py-2.5 px-5 text-xs shadow-glow-brand flex items-center justify-center gap-1.5">
          <Search className="w-3.5 h-3.5" /> Filter
        </button>
      </form>

      {/* ── Partner Grid ── */}
      {isLoading ? (
        <div className="flex flex-col items-center justify-center min-h-[40vh] gap-3">
          <div className="w-10 h-10 rounded-full border-3 border-brand-500 border-t-transparent animate-spin" />
          <p className="text-surface-400 text-xs animate-pulse">Loading industry partners...</p>
        </div>
      ) : partners.length === 0 ? (
        <div className="glass p-12 rounded-2xl border border-white/10 text-center space-y-3">
          <Building2 className="w-12 h-12 text-surface-500 mx-auto" />
          <h3 className="text-lg font-bold text-white">No Industry Partners Found</h3>
          <p className="text-surface-400 text-xs">Try broadening your industry filter or search term.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {partners.map((partner) => (
            <div
              key={partner.id}
              className="glass p-5 rounded-2xl border border-white/10 hover:border-brand-500/30 transition-all flex flex-col justify-between space-y-4"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-brand-300 px-2.5 py-0.5 rounded-full bg-brand-500/10 border border-brand-500/20">
                    {partner.organization_type}
                  </span>
                  <span className="text-xs text-surface-400 flex items-center gap-1">
                    <MapPin className="w-3 h-3 text-surface-500" /> {partner.location}
                  </span>
                </div>

                <h3 className="text-lg font-bold text-white">{partner.name}</h3>

                <p className="text-xs text-surface-400 line-clamp-3 leading-relaxed">
                  {partner.description}
                </p>

                {/* Focus Pills */}
                <div className="space-y-1">
                  <span className="text-[10px] text-surface-500 font-semibold uppercase tracking-wider block">Technology Focus</span>
                  <div className="flex flex-wrap gap-1">
                    {partner.technology_focus?.map((tf, i) => (
                      <span key={i} className="text-[10px] bg-surface-900 text-surface-300 px-2 py-0.5 rounded border border-white/5">
                        {tf}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Collaboration Types */}
                <div className="space-y-1">
                  <span className="text-[10px] text-surface-500 font-semibold uppercase tracking-wider block">Collaboration Modes</span>
                  <div className="flex flex-wrap gap-1">
                    {partner.collaboration_types?.map((ct, i) => (
                      <span key={i} className="text-[10px] bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded border border-emerald-500/20">
                        ✓ {ct}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Card Footer */}
              <div className="pt-4 border-t border-white/5 flex items-center justify-between text-xs">
                <a
                  href={`mailto:${partner.contact_email}`}
                  className="text-brand-400 hover:underline flex items-center gap-1 font-medium text-[11px]"
                >
                  <Mail className="w-3.5 h-3.5" /> Contact R&D
                </a>

                {partner.website_url && (
                  <a
                    href={partner.website_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-secondary text-[11px] py-1 px-2.5 flex items-center gap-1"
                  >
                    Website <ExternalLink className="w-3 h-3" />
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
