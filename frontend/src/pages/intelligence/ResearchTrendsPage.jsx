import { useState, useEffect } from 'react'
import { TrendingUp, Zap, Sparkles, BookOpen, Layers } from 'lucide-react'
import toast from 'react-hot-toast'
import { researchIntelligenceService } from '@/services/researchIntelligenceService'

export default function ResearchTrendsPage() {
  const [trending, setTrending] = useState([])
  const [emerging, setEmerging] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadTrends()
  }, [])

  const loadTrends = async () => {
    try {
      setLoading(true)
      const [tRes, eRes] = await Promise.all([
        researchIntelligenceService.getTrending(10),
        researchIntelligenceService.getEmerging(10),
      ])
      setTrending(tRes)
      setEmerging(eRes)
    } catch (err) {
      toast.error('Failed to load research trends')
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

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl md:text-3xl font-extrabold text-white">
          Research & Technology Trends Intelligence
        </h1>
        <p className="text-surface-400 text-sm mt-1">
          Real-time tracking of high-growth research topics, citation acceleration, and emerging domain frontiers.
        </p>
      </div>

      {/* ── Trending Section ── */}
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-green-400" />
          <h2 className="text-xl font-bold text-white">High-Growth Trending Domains</h2>
        </div>

        <div className="grid md:grid-cols-2 gap-5">
          {trending.map((item) => (
            <div key={item.id} className="glass p-6 space-y-4 hover:border-brand-500/40 transition-all">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <span className="badge badge-brand text-[10px] mb-1">{item.research_domain}</span>
                  <h3 className="text-base font-bold text-white leading-snug">{item.topic_name}</h3>
                </div>
                <span className="badge badge-green text-xs font-extrabold flex-shrink-0">
                  +{item.growth_rate}% YOY
                </span>
              </div>

              <p className="text-xs text-surface-300 leading-relaxed">{item.summary}</p>

              <div className="flex items-center justify-between pt-3 border-t border-white/5 text-xs text-surface-400">
                <span className="flex items-center gap-1">
                  <BookOpen className="w-3.5 h-3.5 text-surface-500" /> {item.paper_count} Tracked Papers
                </span>
                <div className="flex flex-wrap gap-1">
                  {item.key_keywords?.slice(0, 2).map((k) => (
                    <span key={k} className="badge bg-white/5 text-surface-300 text-[10px]">
                      #{k}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── Emerging Section ── */}
      <div className="space-y-4 pt-4 border-t border-white/5">
        <div className="flex items-center gap-2">
          <Zap className="w-5 h-5 text-accent-400" />
          <h2 className="text-xl font-bold text-white">Emerging Frontier Breakthroughs</h2>
        </div>

        <div className="grid md:grid-cols-2 gap-5">
          {emerging.map((item) => (
            <div key={item.id} className="glass p-6 space-y-4 hover:border-accent-500/40 transition-all">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <span className="badge badge-accent text-[10px] mb-1">{item.research_domain}</span>
                  <h3 className="text-base font-bold text-white leading-snug">{item.topic_name}</h3>
                </div>
                <span className="badge badge-accent text-xs font-extrabold flex-shrink-0">
                  +{item.growth_rate}% YOY
                </span>
              </div>

              <p className="text-xs text-surface-300 leading-relaxed">{item.summary}</p>

              <div className="flex items-center justify-between pt-3 border-t border-white/5 text-xs text-surface-400">
                <span className="flex items-center gap-1">
                  <BookOpen className="w-3.5 h-3.5 text-surface-500" /> {item.paper_count} Tracked Papers
                </span>
                <div className="flex flex-wrap gap-1">
                  {item.key_keywords?.slice(0, 2).map((k) => (
                    <span key={k} className="badge bg-white/5 text-surface-300 text-[10px]">
                      #{k}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
