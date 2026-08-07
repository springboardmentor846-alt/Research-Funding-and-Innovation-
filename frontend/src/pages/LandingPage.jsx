import { Link } from 'react-router-dom'
import {
  FlaskConical, ArrowRight, Zap, Shield, BarChart3, Users,
  Globe, BookOpen, Lightbulb, ChevronRight, Star, TrendingUp,
} from 'lucide-react'

const features = [
  {
    icon: Zap,
    title: 'AI-Powered Matching',
    desc: 'Intelligent algorithms connect researchers with the most relevant funding opportunities.',
    color: 'from-brand-500 to-brand-700',
    glow: 'group-hover:shadow-glow-brand',
  },
  {
    icon: Shield,
    title: 'Secure & Compliant',
    desc: 'Enterprise-grade security with RBAC, JWT authentication, and data encryption.',
    color: 'from-emerald-500 to-emerald-700',
    glow: 'group-hover:shadow-[0_0_30px_rgba(16,185,129,0.4)]',
  },
  {
    icon: BarChart3,
    title: 'Patent Analytics',
    desc: 'Deep-dive into patent landscapes, citation networks, and innovation trends.',
    color: 'from-accent-500 to-accent-700',
    glow: 'group-hover:shadow-glow-accent',
  },
  {
    icon: Users,
    title: 'Collaboration Hub',
    desc: 'Connect with fellow researchers, startup founders, and innovation managers globally.',
    color: 'from-orange-500 to-orange-700',
    glow: 'group-hover:shadow-[0_0_30px_rgba(249,115,22,0.4)]',
  },
  {
    icon: Globe,
    title: 'Global Funding Database',
    desc: 'Access thousands of grants, VC funds, and government programmes in one place.',
    color: 'from-sky-500 to-sky-700',
    glow: 'group-hover:shadow-[0_0_30px_rgba(14,165,233,0.4)]',
  },
  {
    icon: TrendingUp,
    title: 'Innovation Tracking',
    desc: 'Monitor technology maturity, market trends, and competitive intelligence.',
    color: 'from-rose-500 to-rose-700',
    glow: 'group-hover:shadow-[0_0_30px_rgba(244,63,94,0.4)]',
  },
]

const roles = [
  { icon: BookOpen,   label: 'Researchers',         desc: 'Discover grants, collaborate on breakthroughs.' },
  { icon: Lightbulb,  label: 'Startup Founders',     desc: 'Access VC intelligence and market insights.'    },
  { icon: BarChart3,  label: 'Innovation Managers',  desc: 'Track portfolios and manage R&D pipelines.'     },
  { icon: Shield,     label: 'Administrators',        desc: 'Govern users, roles, and platform settings.'   },
]

const stats = [
  { value: '50K+',  label: 'Funding Opportunities' },
  { value: '12K+',  label: 'Researchers Onboarded' },
  { value: '$2.4B', label: 'Funding Facilitated'   },
  { value: '98%',   label: 'Match Accuracy'         },
]

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-surface-950 overflow-x-hidden">
      {/* ── Navbar ── */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-surface-950/80 backdrop-blur-xl border-b border-white/5">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center gap-6">
          <Link to="/" className="flex items-center gap-2 flex-shrink-0">
            <div className="w-8 h-8 bg-gradient-to-br from-brand-500 to-accent-500 rounded-lg flex items-center justify-center shadow-glow-brand">
              <FlaskConical className="w-4 h-4 text-white" />
            </div>
            <span className="font-bold gradient-text text-sm">RFIP</span>
          </Link>

          <div className="hidden md:flex items-center gap-1 ml-6">
            {['Features', 'Roles', 'About'].map((item) => (
              <a
                key={item}
                href={`#${item.toLowerCase()}`}
                className="btn-ghost"
              >
                {item}
              </a>
            ))}
          </div>

          <div className="ml-auto flex items-center gap-3">
            <Link to="/login" className="btn-secondary text-sm px-4 py-2">
              Sign In
            </Link>
            <Link to="/register" className="btn-primary text-sm px-4 py-2">
              Get Started <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </nav>

      {/* ── Hero ── */}
      <section className="relative pt-32 pb-24 px-6 flex flex-col items-center text-center">
        {/* Background orbs */}
        <div className="absolute inset-0 pointer-events-none overflow-hidden">
          <div className="absolute top-20 left-1/4 w-80 h-80 bg-brand-600/15 rounded-full blur-3xl animate-float" />
          <div className="absolute top-40 right-1/4 w-60 h-60 bg-accent-600/15 rounded-full blur-3xl animate-float [animation-delay:2s]" />
          <div className="absolute -bottom-20 left-1/2 -translate-x-1/2 w-[600px] h-60 bg-brand-800/10 rounded-full blur-3xl" />
        </div>

        <div className="relative z-10 max-w-4xl mx-auto animate-slide-up">
          <div className="inline-flex items-center gap-2 badge-brand mb-6 py-1.5 px-4 text-xs">
            <Star className="w-3 h-3" />
            Phase 1 — Authentication & User Management
          </div>

          <h1 className="text-4xl md:text-6xl lg:text-7xl font-extrabold leading-[1.1] mb-6">
            Research Funding &{' '}
            <span className="gradient-text">Innovation Intelligence</span>{' '}
            Platform
          </h1>

          <p className="text-lg md:text-xl text-surface-300 max-w-2xl mx-auto mb-10 leading-relaxed">
            Connecting researchers, startups, and innovation managers with
            cutting-edge funding intelligence, AI-powered matching, and
            collaborative tools to accelerate breakthrough discoveries.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/register" className="btn-primary px-8 py-4 text-base">
              Start for Free <ArrowRight className="w-4 h-4" />
            </Link>
            <Link to="/login" className="btn-secondary px-8 py-4 text-base">
              Sign In to Platform
            </Link>
          </div>
        </div>

        {/* Stats row */}
        <div className="relative z-10 mt-20 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-3xl mx-auto w-full">
          {stats.map(({ value, label }) => (
            <div key={label} className="glass p-5 text-center">
              <p className="text-2xl md:text-3xl font-extrabold gradient-text">{value}</p>
              <p className="text-xs text-surface-400 mt-1">{label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Features ── */}
      <section id="features" className="py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-extrabold mb-4">
              Everything you need to{' '}
              <span className="gradient-text">innovate faster</span>
            </h2>
            <p className="text-surface-400 max-w-xl mx-auto">
              A unified platform purpose-built for the entire innovation lifecycle.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map(({ icon: Icon, title, desc, color, glow }) => (
              <div
                key={title}
                className={`group glass p-6 hover:border-white/20 transition-all duration-300 ${glow}`}
              >
                <div
                  className={`w-12 h-12 rounded-xl bg-gradient-to-br ${color} flex items-center justify-center mb-4 shadow-lg group-hover:scale-110 transition-transform duration-300`}
                >
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="font-semibold text-white mb-2">{title}</h3>
                <p className="text-sm text-surface-400 leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Roles ── */}
      <section id="roles" className="py-24 px-6 bg-surface-900/30">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-extrabold mb-4">
              Built for every{' '}
              <span className="gradient-text">role in innovation</span>
            </h2>
            <p className="text-surface-400">
              Role-based access control ensures you see exactly what you need.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 gap-6">
            {roles.map(({ icon: Icon, label, desc }) => (
              <div
                key={label}
                className="glass p-6 flex items-start gap-4 hover:border-brand-500/30 transition-colors group"
              >
                <div className="w-10 h-10 rounded-xl bg-brand-600/20 border border-brand-500/30 flex items-center justify-center flex-shrink-0 group-hover:bg-brand-600/30 transition-colors">
                  <Icon className="w-5 h-5 text-brand-400" />
                </div>
                <div>
                  <h3 className="font-semibold text-white mb-1">{label}</h3>
                  <p className="text-sm text-surface-400">{desc}</p>
                </div>
                <ChevronRight className="w-4 h-4 text-surface-600 ml-auto flex-shrink-0 group-hover:text-brand-400 transition-colors" />
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ── */}
      <section className="py-24 px-6">
        <div className="max-w-3xl mx-auto text-center">
          <div className="glass p-12 relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-brand-600/10 to-accent-600/10 pointer-events-none" />
            <div className="relative z-10">
              <h2 className="text-3xl md:text-4xl font-extrabold mb-4">
                Ready to accelerate{' '}
                <span className="gradient-text">your research?</span>
              </h2>
              <p className="text-surface-400 mb-8">
                Join thousands of researchers and innovators already on the platform.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link to="/register" className="btn-primary px-8 py-4 text-base">
                  Create Free Account <ArrowRight className="w-4 h-4" />
                </Link>
                <Link to="/login" className="btn-secondary px-8 py-4 text-base">
                  I already have an account
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer id="about" className="border-t border-white/5 py-12 px-6">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 bg-gradient-to-br from-brand-500 to-accent-500 rounded-lg flex items-center justify-center">
              <FlaskConical className="w-4 h-4 text-white" />
            </div>
            <span className="font-bold text-sm gradient-text">RFIP Platform</span>
          </div>
          <p className="text-xs text-surface-500">
            © {new Date().getFullYear()} Research Funding & Innovation Intelligence Platform. All rights reserved.
          </p>
          <div className="flex gap-4 text-xs text-surface-500">
            <a href="#" className="hover:text-surface-300 transition-colors">Privacy</a>
            <a href="#" className="hover:text-surface-300 transition-colors">Terms</a>
            <a href="#" className="hover:text-surface-300 transition-colors">Contact</a>
          </div>
        </div>
      </footer>
    </div>
  )
}
