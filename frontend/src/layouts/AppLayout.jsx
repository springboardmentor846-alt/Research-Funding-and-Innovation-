import { useState } from 'react'
import { Outlet, NavLink, Link, useNavigate } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import {
  FlaskConical, LayoutDashboard, User, LogOut, Menu, X,
  Bell, ChevronDown, Shield, BookOpenCheck, Search,
  Coins, Bookmark, Sparkles, BrainCircuit, BookOpen, TrendingUp,
  Lightbulb, FileText, BarChart3, Cpu, Award, Compass, Zap,
  Handshake, Building2, Rocket
} from 'lucide-react'
import toast from 'react-hot-toast'
import { clsx } from 'clsx'

const ROLE_LABELS = {
  researcher:        'Researcher',
  startup_founder:   'Startup Founder',
  innovation_manager:'Innovation Manager',
  administrator:     'Administrator',
}

const ROLE_COLORS = {
  researcher:        'badge-brand',
  startup_founder:   'badge-accent',
  innovation_manager:'badge-green',
  administrator:     'badge-orange',
}

const navItems = [
  { to: '/dashboard',                             icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/notifications',                         icon: Bell,            label: 'Notifications' },
  { to: '/reports',                               icon: FileText,        label: 'Reports & Exports' },
  { to: '/commercialization',                     icon: Handshake,       label: 'Commercialization' },
  { to: '/commercialization/opportunities',       icon: Search,          label: 'Licensing & Joint R&D' },
  { to: '/commercialization/partners',            icon: Building2,       label: 'Industry Partners' },
  { to: '/commercialization/startups',            icon: Rocket,          label: 'Startup Accelerators' },
  { to: '/technology-intelligence',              icon: Cpu,             label: 'Technology Dashboard' },
  { to: '/technology-intelligence/trends',       icon: Zap,             label: 'Tech Trends' },
  { to: '/technology-intelligence/innovation-score', icon: Award,       label: 'Innovation Score' },
  { to: '/technology-intelligence/opportunities', icon: Compass,        label: 'Opportunity Analysis' },
  { to: '/patent-intelligence',                   icon: Lightbulb,       label: 'Patent Intelligence' },
  { to: '/patent-intelligence/search',            icon: FileText,        label: 'Patent Search' },
  { to: '/patent-intelligence/analytics',         icon: BarChart3,      label: 'Patent Analytics' },
  { to: '/research-intelligence',                 icon: BrainCircuit,    label: 'Research Intelligence' },
  { to: '/research-intelligence/search',          icon: BookOpen,        label: 'Literature Search' },
  { to: '/research-intelligence/trends',          icon: TrendingUp,      label: 'Research Trends' },
  { to: '/funding',                               icon: Coins,           label: 'Funding Overview' },
  { to: '/funding/search',                        icon: Search,          label: 'Grant Search' },
  { to: '/funding/bookmarks',                     icon: Bookmark,        label: 'My Saved Grants' },
  { to: '/funding/alerts',                        icon: Bell,            label: 'Funding Alerts' },
  { to: '/admin',                                 icon: Shield,          label: 'Admin Dashboard' },
  { to: '/admin/analytics',                       icon: BarChart3,      label: 'System Analytics' },
  { to: '/admin/users',                           icon: User,            label: 'User Management' },
  { to: '/research-profile',                      icon: BookOpenCheck,   label: 'Research Profile' },
  { to: '/researchers',                           icon: Sparkles,        label: 'Researcher Directory' },
  { to: '/profile',                               icon: User,            label: 'Account Profile' },
]

export default function AppLayout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [profileOpen, setProfileOpen] = useState(false)

  const handleLogout = async () => {
    await logout()
    toast.success('You have been signed out.')
    navigate('/login')
  }

  const NavItems = () => (
    <nav className="flex flex-col gap-1 mt-2">
      {navItems.map(({ to, icon: Icon, label }) => (
        <NavLink
          key={to}
          to={to}
          onClick={() => setSidebarOpen(false)}
          className={({ isActive }) =>
            clsx(
              'flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200',
              isActive
                ? 'bg-brand-600/20 text-brand-300 border border-brand-500/30'
                : 'text-surface-300 hover:text-white hover:bg-white/5'
            )
          }
        >
          <Icon className="w-4 h-4 flex-shrink-0" />
          {label}
        </NavLink>
      ))}
    </nav>
  )

  return (
    <div className="min-h-screen bg-surface-950 flex">
      {/* ── Sidebar ── */}
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/60 z-30 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside
        className={clsx(
          'fixed top-0 left-0 h-full w-64 bg-surface-900 border-r border-white/5 flex flex-col z-40 transition-transform duration-300',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        )}
      >
        {/* Logo */}
        <div className="flex items-center gap-3 px-5 py-5 border-b border-white/5">
          <div className="w-9 h-9 bg-gradient-to-br from-brand-500 to-accent-500 rounded-xl flex items-center justify-center shadow-glow-brand flex-shrink-0">
            <FlaskConical className="w-5 h-5 text-white" />
          </div>
          <div>
            <p className="text-xs font-bold gradient-text leading-none">RFIP</p>
            <p className="text-[10px] text-surface-500 mt-0.5">Innovation Platform</p>
          </div>
          <button
            className="ml-auto lg:hidden p-1 rounded-lg hover:bg-white/5"
            onClick={() => setSidebarOpen(false)}
          >
            <X className="w-4 h-4 text-surface-400" />
          </button>
        </div>

        {/* User mini-card */}
        {user && (
          <div className="mx-4 mt-4 p-3 glass rounded-xl">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-full bg-gradient-to-br from-brand-500 to-accent-500 flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
                {user.full_name?.charAt(0).toUpperCase()}
              </div>
              <div className="min-w-0">
                <p className="text-sm font-medium text-white truncate">{user.full_name}</p>
                <span className={clsx('badge text-[10px] mt-0.5', ROLE_COLORS[user.role])}>
                  {ROLE_LABELS[user.role]}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Nav */}
        <div className="flex-1 px-3 py-4 overflow-y-auto">
          <NavItems />
        </div>

        {/* Bottom logout */}
        <div className="p-4 border-t border-white/5">
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium text-surface-400 hover:text-red-400 hover:bg-red-500/10 transition-all duration-200"
          >
            <LogOut className="w-4 h-4" />
            Sign Out
          </button>
        </div>
      </aside>

      {/* ── Main area ── */}
      <div className="flex-1 lg:ml-64 flex flex-col min-h-screen">
        {/* Top bar */}
        <header className="sticky top-0 z-20 bg-surface-950/80 backdrop-blur-xl border-b border-white/5 px-6 h-16 flex items-center gap-4">
          <button
            className="lg:hidden p-2 rounded-lg hover:bg-white/5 text-surface-400"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="w-5 h-5" />
          </button>

          <div className="flex-1" />

          {/* Notification bell */}
          <button
            className="relative p-2 rounded-xl hover:bg-white/5 text-surface-400 hover:text-white transition-colors"
            aria-label="Notifications"
          >
            <Bell className="w-5 h-5" />
            <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 bg-accent-500 rounded-full" />
          </button>

          {/* Profile dropdown */}
          <div className="relative">
            <button
              id="profile-menu-btn"
              onClick={() => setProfileOpen((o) => !o)}
              className="flex items-center gap-2 p-1.5 rounded-xl hover:bg-white/5 transition-colors"
            >
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-brand-500 to-accent-500 flex items-center justify-center text-white font-bold text-sm">
                {user?.full_name?.charAt(0).toUpperCase()}
              </div>
              <ChevronDown className="w-3.5 h-3.5 text-surface-400" />
            </button>

            {profileOpen && (
              <>
                <div className="fixed inset-0 z-10" onClick={() => setProfileOpen(false)} />
                <div className="absolute right-0 top-12 w-52 glass-dark rounded-xl border border-white/10 shadow-glass z-20 overflow-hidden animate-slide-down">
                  <div className="px-4 py-3 border-b border-white/5">
                    <p className="text-sm font-medium text-white truncate">{user?.full_name}</p>
                    <p className="text-xs text-surface-400 truncate">{user?.email}</p>
                  </div>
                  <div className="p-1">
                    <Link
                      to="/profile"
                      onClick={() => setProfileOpen(false)}
                      className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-surface-300 hover:text-white hover:bg-white/5 transition-colors"
                    >
                      <User className="w-4 h-4" />
                      Profile
                    </Link>
                    {user?.is_superuser && (
                      <Link
                        to="/admin"
                        onClick={() => setProfileOpen(false)}
                        className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-surface-300 hover:text-white hover:bg-white/5 transition-colors"
                      >
                        <Shield className="w-4 h-4" />
                        Admin Panel
                      </Link>
                    )}
                    <button
                      onClick={handleLogout}
                      className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-red-400 hover:bg-red-500/10 transition-colors"
                    >
                      <LogOut className="w-4 h-4" />
                      Sign Out
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 p-6 animate-fade-in">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
