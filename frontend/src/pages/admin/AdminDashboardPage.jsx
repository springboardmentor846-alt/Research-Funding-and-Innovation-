import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  Shield, Users, BookOpenCheck, Coins, BookOpen,
  Lightbulb, Cpu, Handshake, BarChart3, Bell, FileText,
  TrendingUp, ArrowRight, UserCheck, Sparkles
} from 'lucide-react'
import { reportsNotificationsService } from '@/services/reportsNotificationsService'
import toast from 'react-hot-toast'

export default function AdminDashboardPage() {
  const [stats, setStats] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      setIsLoading(true)
      const data = await reportsNotificationsService.getAdminStats()
      setStats(data)
    } catch (err) {
      toast.error('Failed to load admin statistics.')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <div className="w-12 h-12 rounded-full border-4 border-brand-500 border-t-transparent animate-spin" />
        <p className="text-surface-400 text-sm animate-pulse">Loading Platform Admin Intelligence...</p>
      </div>
    )
  }

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* ── Header ── */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 glass p-6 rounded-2xl border border-white/10">
        <div>
          <div className="flex items-center gap-2 text-amber-400 font-semibold text-xs tracking-wider uppercase mb-1">
            <Shield className="w-4 h-4" /> Phase 8 · Executive Control Center
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white">Platform Admin Dashboard</h1>
          <p className="text-surface-400 text-sm mt-1">
            Comprehensive platform statistics, entity analytics, system metrics, and administrative user controls.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link to="/admin/analytics" className="btn-secondary text-xs flex items-center gap-1.5">
            <BarChart3 className="w-4 h-4" /> System Analytics
          </Link>
          <Link to="/admin/users" className="btn-primary text-xs shadow-glow-brand flex items-center gap-1.5">
            <Users className="w-4 h-4" /> User Management
          </Link>
        </div>
      </div>

      {/* ── Entity Counts Grid ── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass p-5 rounded-2xl border border-white/5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-brand-500/20 text-brand-400 flex items-center justify-center flex-shrink-0">
            <Users className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs text-surface-400 font-medium">Total Registered Users</p>
            <p className="text-2xl font-bold text-white mt-0.5">{stats?.total_users || 0}</p>
            <span className="text-[10px] text-brand-400 font-medium">+18% this month</span>
          </div>
        </div>

        <div className="glass p-5 rounded-2xl border border-white/5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center flex-shrink-0">
            <BookOpenCheck className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs text-surface-400 font-medium">Research Profiles</p>
            <p className="text-2xl font-bold text-emerald-400 mt-0.5">{stats?.research_profiles || 0}</p>
            <span className="text-[10px] text-emerald-500/80 font-medium">Academic & Founders</span>
          </div>
        </div>

        <div className="glass p-5 rounded-2xl border border-white/5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-amber-500/20 text-amber-400 flex items-center justify-center flex-shrink-0">
            <Coins className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs text-surface-400 font-medium">Funding Grants</p>
            <p className="text-2xl font-bold text-amber-400 mt-0.5">{stats?.funding_opportunities || 0}</p>
            <span className="text-[10px] text-amber-500/80 font-medium">NSF, DARPA, NIH</span>
          </div>
        </div>

        <div className="glass p-5 rounded-2xl border border-white/5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-accent-500/20 text-accent-400 flex items-center justify-center flex-shrink-0">
            <BookOpen className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs text-surface-400 font-medium">Research Papers</p>
            <p className="text-2xl font-bold text-accent-300 mt-0.5">{stats?.research_papers || 0}</p>
            <span className="text-[10px] text-surface-500">Indexed & Open Access</span>
          </div>
        </div>

        <div className="glass p-5 rounded-2xl border border-white/5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-amber-500/20 text-amber-400 flex items-center justify-center flex-shrink-0">
            <Lightbulb className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs text-surface-400 font-medium">Patents</p>
            <p className="text-2xl font-bold text-white mt-0.5">{stats?.patents || 0}</p>
            <span className="text-[10px] text-surface-500">USPTO & Google Patents</span>
          </div>
        </div>

        <div className="glass p-5 rounded-2xl border border-white/5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-brand-500/20 text-brand-400 flex items-center justify-center flex-shrink-0">
            <Cpu className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs text-surface-400 font-medium">Technology Trends</p>
            <p className="text-2xl font-bold text-brand-300 mt-0.5">{stats?.technology_trends || 0}</p>
            <span className="text-[10px] text-surface-500">TRL 1-9 Monitored</span>
          </div>
        </div>

        <div className="glass p-5 rounded-2xl border border-white/5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center flex-shrink-0">
            <Handshake className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs text-surface-400 font-medium">Commercialization Opps</p>
            <p className="text-2xl font-bold text-emerald-400 mt-0.5">{stats?.commercialization_opportunities || 0}</p>
            <span className="text-[10px] text-surface-500">Licensing & Joint R&D</span>
          </div>
        </div>

        <div className="glass p-5 rounded-2xl border border-white/5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-accent-500/20 text-accent-400 flex items-center justify-center flex-shrink-0">
            <UserCheck className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs text-surface-400 font-medium">Active Collaborations</p>
            <p className="text-2xl font-bold text-accent-300 mt-0.5">{stats?.active_collaborations || 0}</p>
            <span className="text-[10px] text-surface-500">Inquiries & Bookmarks</span>
          </div>
        </div>
      </div>

      {/* ── Quick Control Links ── */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link
          to="/admin/analytics"
          className="glass p-6 rounded-2xl border border-white/10 hover:border-brand-500/30 transition-all space-y-3 group"
        >
          <div className="w-10 h-10 rounded-xl bg-brand-500/20 text-brand-400 flex items-center justify-center">
            <BarChart3 className="w-5 h-5" />
          </div>
          <h3 className="text-base font-bold text-white group-hover:text-brand-300 transition-colors">
            System Analytics & Visualizations
          </h3>
          <p className="text-xs text-surface-400 leading-relaxed">
            Detailed breakdown of user growth, research domain distributions, funding agencies, and innovation scores.
          </p>
          <span className="text-xs text-brand-400 font-semibold flex items-center gap-1">
            View System Charts <ArrowRight className="w-3.5 h-3.5" />
          </span>
        </Link>

        <Link
          to="/reports"
          className="glass p-6 rounded-2xl border border-white/10 hover:border-amber-500/30 transition-all space-y-3 group"
        >
          <div className="w-10 h-10 rounded-xl bg-amber-500/20 text-amber-400 flex items-center justify-center">
            <FileText className="w-5 h-5" />
          </div>
          <h3 className="text-base font-bold text-white group-hover:text-amber-300 transition-colors">
            Reports & Export Center
          </h3>
          <p className="text-xs text-surface-400 leading-relaxed">
            Generate printable PDF reports and export CSV spreadsheets for Research Summaries, Grants, and Patents.
          </p>
          <span className="text-xs text-amber-400 font-semibold flex items-center gap-1">
            Export Reports <ArrowRight className="w-3.5 h-3.5" />
          </span>
        </Link>

        <Link
          to="/notifications"
          className="glass p-6 rounded-2xl border border-white/10 hover:border-emerald-500/30 transition-all space-y-3 group"
        >
          <div className="w-10 h-10 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
            <Bell className="w-5 h-5" />
          </div>
          <h3 className="text-base font-bold text-white group-hover:text-emerald-300 transition-colors">
            Notifications Center
          </h3>
          <p className="text-xs text-surface-400 leading-relaxed">
            Manage funding deadline alerts, AI paper recommendations, patent citation updates, and collaboration requests.
          </p>
          <span className="text-xs text-emerald-400 font-semibold flex items-center gap-1">
            Open Notifications <ArrowRight className="w-3.5 h-3.5" />
          </span>
        </Link>
      </div>
    </div>
  )
}
