import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  BarChart3, TrendingUp, Layers, Coins, Lightbulb,
  Award, ArrowLeft, Shield, Users
} from 'lucide-react'
import { reportsNotificationsService } from '@/services/reportsNotificationsService'
import toast from 'react-hot-toast'

export default function SystemAnalyticsPage() {
  const [data, setData] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchAnalytics()
  }, [])

  const fetchAnalytics = async () => {
    try {
      setIsLoading(true)
      const analytics = await reportsNotificationsService.getSystemAnalytics()
      setData(analytics)
    } catch (err) {
      toast.error('Failed to load system analytics.')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <div className="w-12 h-12 rounded-full border-4 border-brand-500 border-t-transparent animate-spin" />
        <p className="text-surface-400 text-sm animate-pulse">Compiling System Analytics...</p>
      </div>
    )
  }

  const {
    user_growth = [],
    domain_distribution = [],
    funding_distribution = [],
    patent_statistics = [],
    innovation_score_distribution = [],
  } = data || {}

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* ── Navigation & Header ── */}
      <div className="space-y-4">
        <Link
          to="/admin"
          className="inline-flex items-center gap-2 text-xs font-semibold text-surface-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Admin Control Center
        </Link>

        <div>
          <div className="flex items-center gap-2 text-brand-400 font-semibold text-xs tracking-wider uppercase mb-1">
            <BarChart3 className="w-4 h-4" /> System Analytics & Data Visualizations
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white">Platform Intelligence Analytics</h1>
          <p className="text-surface-400 text-sm mt-1">
            Visual metrics covering user growth trajectories, research domain concentration, grant capital distribution, and innovation readiness.
          </p>
        </div>
      </div>

      {/* ── User Growth & Research Domain Distribution ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* User Growth Chart */}
        <div className="glass p-6 rounded-2xl border border-white/10 space-y-4">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-brand-400" /> Platform User Growth Trajectory
          </h2>

          <div className="space-y-4 pt-2">
            {user_growth.map((item, i) => (
              <div key={i} className="space-y-1.5 text-xs">
                <div className="flex justify-between font-medium">
                  <span className="text-surface-300">{item.label} 2025</span>
                  <span className="text-brand-300 font-bold">{item.value} Users</span>
                </div>
                <div className="w-full h-3 bg-surface-900 rounded-full overflow-hidden border border-white/5">
                  <div
                    className="h-full bg-gradient-to-r from-brand-600 to-accent-500 rounded-full transition-all duration-500"
                    style={{ width: `${Math.min((item.value / 1250) * 100, 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Research Domains Breakdown */}
        <div className="glass p-6 rounded-2xl border border-white/10 space-y-4">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Layers className="w-5 h-5 text-accent-400" /> Research Domains Share
          </h2>

          <div className="space-y-4 pt-2">
            {domain_distribution.map((item, i) => (
              <div key={i} className="space-y-1.5 text-xs">
                <div className="flex justify-between font-medium">
                  <span className="text-surface-300 truncate max-w-[200px]">{item.domain}</span>
                  <span className="text-accent-300 font-bold">{item.percentage}% ({item.count})</span>
                </div>
                <div className="w-full h-3 bg-surface-900 rounded-full overflow-hidden border border-white/5">
                  <div
                    className="h-full bg-gradient-to-r from-accent-600 to-emerald-500 rounded-full transition-all duration-500"
                    style={{ width: `${item.percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Funding, Patent & Innovation Distributions ── */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Funding Agency Capital */}
        <div className="glass p-6 rounded-2xl border border-white/10 space-y-4">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <Coins className="w-4 h-4 text-amber-400" /> Grant Capital ($M)
          </h2>
          <div className="space-y-3 pt-1 text-xs">
            {funding_distribution.map((item, i) => (
              <div key={i} className="space-y-1">
                <div className="flex justify-between">
                  <span className="text-surface-400 truncate">{item.label}</span>
                  <span className="text-amber-400 font-bold">${item.value}M</span>
                </div>
                <div className="w-full h-2 bg-surface-900 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-amber-500 rounded-full"
                    style={{ width: `${(item.value / 45) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Patent Statistics */}
        <div className="glass p-6 rounded-2xl border border-white/10 space-y-4">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <Lightbulb className="w-4 h-4 text-brand-400" /> Patent Portfolio (%)
          </h2>
          <div className="space-y-3 pt-1 text-xs">
            {patent_statistics.map((item, i) => (
              <div key={i} className="space-y-1">
                <div className="flex justify-between">
                  <span className="text-surface-400 truncate">{item.label}</span>
                  <span className="text-brand-300 font-bold">{item.value}%</span>
                </div>
                <div className="w-full h-2 bg-surface-900 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-brand-500 rounded-full"
                    style={{ width: `${item.value}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Innovation Score Distribution */}
        <div className="glass p-6 rounded-2xl border border-white/10 space-y-4">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <Award className="w-4 h-4 text-emerald-400" /> Innovation Score Tiers
          </h2>
          <div className="space-y-3 pt-1 text-xs">
            {innovation_score_distribution.map((item, i) => (
              <div key={i} className="space-y-1">
                <div className="flex justify-between">
                  <span className="text-surface-400 truncate">{item.label}</span>
                  <span className="text-emerald-400 font-bold">{item.value}%</span>
                </div>
                <div className="w-full h-2 bg-surface-900 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-emerald-500 rounded-full"
                    style={{ width: `${item.value}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
