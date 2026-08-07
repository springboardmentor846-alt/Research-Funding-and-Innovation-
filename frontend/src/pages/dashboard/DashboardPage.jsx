import { useAuth } from '@/context/AuthContext'
import {
  LayoutDashboard, FlaskConical, TrendingUp, Lightbulb,
  Globe, BarChart3, ArrowRight, Clock, Bell,
} from 'lucide-react'
import { Link } from 'react-router-dom'

const ROLE_LABELS = {
  researcher:        'Researcher',
  startup_founder:   'Startup Founder',
  innovation_manager:'Innovation Manager',
  administrator:     'Administrator',
}

const comingSoon = [
  { icon: FlaskConical, label: 'Funding Opportunities',   desc: 'Browse & apply for grants' },
  { icon: TrendingUp,   label: 'Innovation Trends',       desc: 'AI-powered market intelligence' },
  { icon: Lightbulb,    label: 'Patent Analytics',         desc: 'Landscape analysis & citations' },
  { icon: Globe,        label: 'Global Collaboration Hub', desc: 'Connect with worldwide innovators' },
  { icon: BarChart3,    label: 'Funding Recommender',      desc: 'Personalised funding matches' },
]

export default function DashboardPage() {
  const { user } = useAuth()

  const hour = new Date().getHours()
  const greeting = hour < 12 ? 'Good morning' : hour < 18 ? 'Good afternoon' : 'Good evening'

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* ── Welcome ── */}
      <div className="relative glass p-8 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-brand-600/10 to-accent-600/5 pointer-events-none" />
        <div className="absolute top-0 right-0 w-64 h-64 bg-brand-500/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/4 pointer-events-none" />
        <div className="relative z-10 flex flex-col sm:flex-row sm:items-center gap-4">
          <div className="flex-1">
            <p className="text-surface-400 text-sm">{greeting},</p>
            <h1 className="text-2xl md:text-3xl font-extrabold text-white mt-1">
              {user?.full_name} 👋
            </h1>
            <p className="text-surface-400 text-sm mt-2">
              You're signed in as a{' '}
              <span className="text-brand-400 font-medium">{ROLE_LABELS[user?.role]}</span>.
              Phase 1 (Authentication) is live.
            </p>
          </div>
          <div className="flex-shrink-0">
            <Link to="/profile" className="btn-primary px-5 py-2.5 text-sm">
              Edit Profile <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </div>

      {/* ── Quick stats ── */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Login Count',  value: user?.login_count ?? 1, sub: 'total sessions' },
          { label: 'Role',         value: ROLE_LABELS[user?.role] ?? '—', sub: 'access level' },
          { label: 'Account',      value: user?.is_verified ? 'Verified' : 'Unverified', sub: 'email status' },
          { label: 'Status',       value: user?.is_active ? 'Active' : 'Inactive', sub: 'account status' },
        ].map(({ label, value, sub }) => (
          <div key={label} className="glass p-5">
            <p className="text-xs text-surface-400 uppercase tracking-wider">{label}</p>
            <p className="text-xl font-bold text-white mt-1 truncate">{value}</p>
            <p className="text-xs text-surface-500 mt-0.5">{sub}</p>
          </div>
        ))}
      </div>

      {/* ── Coming soon modules ── */}
      <div>
        <div className="flex items-center gap-3 mb-4">
          <Clock className="w-5 h-5 text-brand-400" />
          <h2 className="text-lg font-semibold text-white">Coming in Phase 2+</h2>
        </div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {comingSoon.map(({ icon: Icon, label, desc }) => (
            <div
              key={label}
              className="glass p-5 flex items-start gap-4 opacity-60 hover:opacity-80 transition-opacity group"
            >
              <div className="w-10 h-10 rounded-xl bg-brand-600/20 border border-brand-500/20 flex items-center justify-center flex-shrink-0">
                <Icon className="w-5 h-5 text-brand-400" />
              </div>
              <div className="min-w-0">
                <p className="font-medium text-white text-sm">{label}</p>
                <p className="text-xs text-surface-500 mt-0.5">{desc}</p>
              </div>
              <div className="ml-auto flex-shrink-0">
                <span className="badge bg-surface-800 text-surface-400 border border-white/5 text-[10px]">
                  Soon
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── Notification placeholder ── */}
      <div className="glass p-6">
        <div className="flex items-center gap-3 mb-4">
          <Bell className="w-5 h-5 text-accent-400" />
          <h2 className="text-lg font-semibold text-white">Notifications</h2>
        </div>
        <div className="flex flex-col items-center py-8 text-center">
          <div className="w-12 h-12 rounded-full bg-surface-800 flex items-center justify-center mb-3">
            <Bell className="w-6 h-6 text-surface-500" />
          </div>
          <p className="text-surface-400 text-sm">No notifications yet.</p>
          <p className="text-surface-500 text-xs mt-1">
            Funding alerts and collaboration invites will appear here.
          </p>
        </div>
      </div>
    </div>
  )
}
