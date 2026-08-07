import { Outlet, Link } from 'react-router-dom'
import { FlaskConical } from 'lucide-react'

/**
 * Minimal layout for auth pages (login, register, etc.)
 * Features an animated gradient background and centered card.
 */
export default function AuthLayout() {
  return (
    <div className="min-h-screen gradient-bg flex flex-col">
      {/* Decorative orbs */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none" aria-hidden>
        <div className="absolute -top-40 -left-40 w-96 h-96 bg-brand-600/20 rounded-full blur-3xl animate-pulse-slow" />
        <div className="absolute -bottom-40 -right-40 w-96 h-96 bg-accent-600/20 rounded-full blur-3xl animate-pulse-slow [animation-delay:1.5s]" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-72 h-72 bg-brand-800/10 rounded-full blur-3xl" />
      </div>

      {/* Header */}
      <header className="relative z-10 px-6 py-5">
        <Link to="/" className="inline-flex items-center gap-2 group">
          <div className="w-8 h-8 bg-gradient-to-br from-brand-500 to-accent-500 rounded-lg flex items-center justify-center shadow-glow-brand group-hover:shadow-glow-accent transition-shadow duration-300">
            <FlaskConical className="w-4 h-4 text-white" />
          </div>
          <span className="font-bold text-sm gradient-text">RFIP</span>
        </Link>
      </header>

      {/* Page content */}
      <main className="relative z-10 flex-1 flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-md animate-slide-up">
          <Outlet />
        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 text-center py-4 text-xs text-surface-500">
        © {new Date().getFullYear()} RFIP Platform. All rights reserved.
      </footer>
    </div>
  )
}
