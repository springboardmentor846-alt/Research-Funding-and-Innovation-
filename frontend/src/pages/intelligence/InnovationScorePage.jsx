import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  Award, Gauge, Sparkles, CheckCircle2, TrendingUp,
  FileText, ShieldCheck, Layers, BookOpenCheck, ArrowRight,
  AlertCircle, Target
} from 'lucide-react'
import { technologyService } from '@/services/technologyService'
import toast from 'react-hot-toast'

export default function InnovationScorePage() {
  const [scoreData, setScoreData] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchScore()
  }, [])

  const fetchScore = async () => {
    try {
      setIsLoading(true)
      const data = await technologyService.getInnovationScore()
      setScoreData(data)
    } catch (err) {
      toast.error('Failed to calculate Innovation Score.')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <div className="w-12 h-12 rounded-full border-4 border-brand-500 border-t-transparent animate-spin" />
        <p className="text-surface-400 text-sm animate-pulse">Evaluating Research & IP Portfolio Metrics...</p>
      </div>
    )
  }

  const {
    overall_score,
    trl_level,
    research_strength,
    patent_strength,
    commercial_potential,
    recommendation_summary,
    breakdown_details,
  } = scoreData || {}

  const trlStages = [
    { level: 1, name: 'TRL 1-3', desc: 'Basic Principles & Proof of Concept' },
    { level: 4, name: 'TRL 4-6', desc: 'Lab Validation & Prototype Testing' },
    { level: 7, name: 'TRL 7-9', desc: 'System Deployment & Commercialization' },
  ]

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* ── Header ── */}
      <div>
        <div className="flex items-center gap-2 text-brand-400 font-semibold text-xs tracking-wider uppercase mb-1">
          <Award className="w-4 h-4" /> Automated Portfolio Assessment
        </div>
        <h1 className="text-2xl md:text-3xl font-extrabold text-white">Innovation Score & TRL Assessment</h1>
        <p className="text-surface-400 text-sm mt-1">
          Quantitative evaluation synthesized from your Research Profile, scientific publications, patent portfolio, and market relevance.
        </p>
      </div>

      {/* ── Main Innovation Score Banner ── */}
      <div className="glass p-8 rounded-2xl border border-white/10 bg-gradient-to-br from-surface-900 via-brand-950/30 to-accent-950/20 space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-center">
          {/* Main Score Gauge */}
          <div className="flex flex-col items-center justify-center p-6 glass rounded-2xl border border-white/10 text-center space-y-2">
            <div className="relative flex items-center justify-center w-36 h-36 rounded-full bg-gradient-to-tr from-brand-600 to-accent-500 p-1 shadow-glow-brand">
              <div className="w-full h-full bg-surface-950 rounded-full flex flex-col items-center justify-center">
                <span className="text-4xl font-extrabold text-white">{overall_score}</span>
                <span className="text-[10px] text-surface-400 uppercase tracking-widest font-semibold mt-0.5">Out of 100</span>
              </div>
            </div>
            <div className="pt-2">
              <span className="badge badge-accent text-xs font-bold px-3 py-1">
                {overall_score >= 80 ? '🌟 High Innovation Index' : overall_score >= 60 ? '⚡ Strong Potential' : '📈 Developing Portfolio'}
              </span>
            </div>
          </div>

          {/* Sub-score Pillars (2 cols) */}
          <div className="md:col-span-2 space-y-4">
            <div className="space-y-1.5">
              <div className="flex justify-between items-center text-xs">
                <span className="font-semibold text-surface-200 flex items-center gap-1.5">
                  <FileText className="w-4 h-4 text-brand-400" /> Research Strength (Publications & Citations)
                </span>
                <span className="text-brand-300 font-bold">{research_strength} / 100</span>
              </div>
              <div className="w-full bg-surface-900 rounded-full h-2.5 overflow-hidden">
                <div className="bg-brand-500 h-full rounded-full" style={{ width: `${research_strength}%` }} />
              </div>
            </div>

            <div className="space-y-1.5">
              <div className="flex justify-between items-center text-xs">
                <span className="font-semibold text-surface-200 flex items-center gap-1.5">
                  <ShieldCheck className="w-4 h-4 text-amber-400" /> Patent Strength (IP Portfolio & Grants)
                </span>
                <span className="text-amber-400 font-bold">{patent_strength} / 100</span>
              </div>
              <div className="w-full bg-surface-900 rounded-full h-2.5 overflow-hidden">
                <div className="bg-amber-500 h-full rounded-full" style={{ width: `${patent_strength}%` }} />
              </div>
            </div>

            <div className="space-y-1.5">
              <div className="flex justify-between items-center text-xs">
                <span className="font-semibold text-surface-200 flex items-center gap-1.5">
                  <TrendingUp className="w-4 h-4 text-emerald-400" /> Commercial Potential (Market Alignment)
                </span>
                <span className="text-emerald-400 font-bold">{commercial_potential} / 100</span>
              </div>
              <div className="w-full bg-surface-900 rounded-full h-2.5 overflow-hidden">
                <div className="bg-emerald-500 h-full rounded-full" style={{ width: `${commercial_potential}%` }} />
              </div>
            </div>
          </div>
        </div>

        {/* AI Recommendation Summary Box */}
        <div className="p-4 bg-surface-950/80 rounded-xl border border-white/5 space-y-1">
          <div className="flex items-center gap-2 text-accent-400 font-bold text-xs">
            <Sparkles className="w-4 h-4" /> AI Strategic Recommendation Summary
          </div>
          <p className="text-xs text-surface-300 leading-relaxed italic">
            "{recommendation_summary}"
          </p>
        </div>
      </div>

      {/* ── Technology Readiness Level (TRL) Breakdown ── */}
      <div className="glass p-6 rounded-2xl border border-white/10 space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Gauge className="w-5 h-5 text-brand-400" />
            Assessed Technology Readiness Level (TRL 1 – 9)
          </h2>
          <span className="text-xs font-bold text-brand-300 bg-brand-500/10 px-3 py-1 rounded-full border border-brand-500/20">
            Current Level: TRL-{trl_level}
          </span>
        </div>

        {/* TRL Stage Bar */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {trlStages.map((stage) => {
            const isActive = trl_level >= stage.level
            return (
              <div
                key={stage.name}
                className={`p-4 rounded-xl border transition-all space-y-2 ${
                  isActive
                    ? 'bg-brand-500/10 border-brand-500/30 text-white'
                    : 'bg-surface-900/50 border-white/5 text-surface-500'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-bold">{stage.name}</span>
                  {isActive && <CheckCircle2 className="w-4 h-4 text-emerald-400" />}
                </div>
                <p className="text-xs text-surface-400">{stage.desc}</p>
              </div>
            )
          })}
        </div>
      </div>

      {/* ── Portfolio Metrics & Strengths Grid ── */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Input Portfolio Metrics */}
        <div className="glass p-6 rounded-2xl border border-white/10 space-y-4">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <BookOpenCheck className="w-5 h-5 text-accent-400" />
            Portfolio Metrics Input
          </h2>

          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="p-3 bg-surface-900 rounded-xl border border-white/5">
              <span className="text-surface-500 block">Publications</span>
              <span className="text-xl font-bold text-white mt-1 block">{breakdown_details?.publications_count || 0}</span>
            </div>

            <div className="p-3 bg-surface-900 rounded-xl border border-white/5">
              <span className="text-surface-500 block">Total Citations</span>
              <span className="text-xl font-bold text-emerald-400 mt-1 block">{breakdown_details?.total_citations || 0}</span>
            </div>

            <div className="p-3 bg-surface-900 rounded-xl border border-white/5">
              <span className="text-surface-500 block">H-Index</span>
              <span className="text-xl font-bold text-amber-400 mt-1 block">{breakdown_details?.h_index || 0}</span>
            </div>

            <div className="p-3 bg-surface-900 rounded-xl border border-white/5">
              <span className="text-surface-500 block">Granted Patents</span>
              <span className="text-xl font-bold text-brand-300 mt-1 block">{breakdown_details?.granted_patents_count || 0}</span>
            </div>
          </div>
        </div>

        {/* Key Strengths & Growth Areas */}
        <div className="glass p-6 rounded-2xl border border-white/10 space-y-4">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Target className="w-5 h-5 text-emerald-400" />
            Strengths & Growth Opportunities
          </h2>

          <div className="space-y-3 text-xs">
            <div>
              <p className="text-emerald-400 font-semibold mb-1.5 flex items-center gap-1">
                ✓ Identified Portfolio Strengths:
              </p>
              <ul className="space-y-1 pl-4 list-disc text-surface-300">
                {breakdown_details?.strengths?.map((s, i) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            </div>

            <div className="pt-2 border-t border-white/5">
              <p className="text-amber-400 font-semibold mb-1.5 flex items-center gap-1">
                💡 Recommended Growth Actions:
              </p>
              <ul className="space-y-1 pl-4 list-disc text-surface-300">
                {breakdown_details?.growth_areas?.map((g, i) => (
                  <li key={i}>{g}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
