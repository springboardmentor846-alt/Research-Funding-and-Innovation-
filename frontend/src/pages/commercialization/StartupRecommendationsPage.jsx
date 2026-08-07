import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  Rocket, Search, ExternalLink, DollarSign, Clock,
  Award, ShieldCheck, CheckCircle2, Layers
} from 'lucide-react'
import { commercializationService } from '@/services/commercializationService'
import toast from 'react-hot-toast'

export default function StartupRecommendationsPage() {
  const [domain, setDomain] = useState('')
  const [programs, setPrograms] = useState([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchStartupPrograms()
  }, [domain])

  const fetchStartupPrograms = async () => {
    try {
      setIsLoading(true)
      const data = await commercializationService.getStartupPrograms({
        domain: domain.trim() || undefined,
      })
      setPrograms(data)
    } catch (err) {
      toast.error('Failed to load startup programs.')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* ── Header ── */}
      <div>
        <div className="flex items-center gap-2 text-amber-400 font-semibold text-xs tracking-wider uppercase mb-1">
          <Rocket className="w-4 h-4" /> Venture Acceleration & Spinout Programs
        </div>
        <h1 className="text-2xl md:text-3xl font-extrabold text-white">Startup Accelerators & Incubators</h1>
        <p className="text-surface-400 text-sm mt-1">
          Explore top global seed funds, corporate incubators, equity-free grants, and spinout acceleration cohorts.
        </p>
      </div>

      {/* ── Filter ── */}
      <div className="glass p-5 rounded-2xl border border-white/10 flex items-center justify-between gap-4">
        <span className="text-xs font-bold text-white flex items-center gap-2">
          <Layers className="w-4 h-4 text-brand-400" /> Filter by Technology Domain
        </span>
        <input
          type="text"
          value={domain}
          onChange={(e) => setDomain(e.target.value)}
          placeholder="e.g. AI, Quantum, CleanTech, Bio..."
          className="bg-surface-900 border border-white/10 rounded-xl px-3 py-2 text-xs text-white placeholder-surface-500 focus:border-brand-500 focus:outline-none w-full max-w-xs"
        />
      </div>

      {/* ── Program Cards Grid ── */}
      {isLoading ? (
        <div className="flex flex-col items-center justify-center min-h-[40vh] gap-3">
          <div className="w-10 h-10 rounded-full border-3 border-brand-500 border-t-transparent animate-spin" />
          <p className="text-surface-400 text-xs animate-pulse">Loading startup programs...</p>
        </div>
      ) : programs.length === 0 ? (
        <div className="glass p-12 rounded-2xl border border-white/10 text-center space-y-3">
          <Rocket className="w-12 h-12 text-surface-500 mx-auto" />
          <h3 className="text-lg font-bold text-white">No Startup Programs Found</h3>
          <p className="text-surface-400 text-xs">Try searching for a different technology domain.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {programs.map((program) => (
            <div
              key={program.id}
              className="glass p-6 rounded-2xl border border-white/10 hover:border-amber-500/30 transition-all flex flex-col justify-between space-y-4"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/30">
                    {program.program_type}
                  </span>
                  <span className="text-xs text-surface-400">
                    Organizer: <strong className="text-white">{program.organizer}</strong>
                  </span>
                </div>

                <h3 className="text-lg font-bold text-white">{program.program_name}</h3>

                {/* Key Metrics Row */}
                <div className="grid grid-cols-3 gap-2 p-3 bg-surface-900/90 rounded-xl border border-white/5 text-center text-xs">
                  <div>
                    <span className="text-[10px] text-surface-500 block">Funding</span>
                    <span className="font-bold text-emerald-400 mt-0.5 block">
                      {program.funding_amount_usd > 0 ? `$${(program.funding_amount_usd / 1000).toFixed(0)}k` : 'Grant Credits'}
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] text-surface-500 block">Equity</span>
                    <span className="font-bold text-white mt-0.5 block">
                      {program.equity_taken_pct > 0 ? `${program.equity_taken_pct}% Equity` : '0% Equity-Free'}
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] text-surface-500 block">Duration</span>
                    <span className="font-bold text-amber-300 mt-0.5 block">{program.duration_months} Months</span>
                  </div>
                </div>

                <p className="text-xs text-surface-300 leading-relaxed">{program.description}</p>

                <div className="p-3 bg-brand-950/40 rounded-xl border border-brand-500/20 space-y-1">
                  <span className="text-[10px] text-brand-400 font-bold uppercase tracking-wider block">Eligibility Criteria</span>
                  <p className="text-xs text-brand-200">{program.eligibility_criteria}</p>
                </div>
              </div>

              {/* Card Footer */}
              <div className="pt-4 border-t border-white/5 flex items-center justify-between text-xs text-surface-400">
                <span>Deadline: <strong className="text-white">{program.deadline || 'Rolling Admissions'}</strong></span>

                {program.website_url && (
                  <a
                    href={program.website_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-primary text-xs py-1.5 px-3 flex items-center gap-1 shadow-glow-brand"
                  >
                    Apply Now <ExternalLink className="w-3.5 h-3.5" />
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
