import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { CheckCircle, AlertCircle, Loader2 } from 'lucide-react'
import { authService } from '@/services/authService'

export default function VerifyEmailPage() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')
  const [status, setStatus] = useState('loading') // loading | success | error

  useEffect(() => {
    if (!token) { setStatus('error'); return }
    authService.verifyEmail(token)
      .then(() => setStatus('success'))
      .catch(() => setStatus('error'))
  }, [token])

  if (status === 'loading') {
    return (
      <div className="card text-center">
        <Loader2 className="w-10 h-10 animate-spin text-brand-400 mx-auto mb-4" />
        <p className="text-surface-400">Verifying your email…</p>
      </div>
    )
  }

  if (status === 'success') {
    return (
      <div className="card text-center">
        <div className="w-16 h-16 bg-emerald-500/20 border border-emerald-500/30 rounded-full flex items-center justify-center mx-auto mb-4">
          <CheckCircle className="w-8 h-8 text-emerald-400" />
        </div>
        <h2 className="text-xl font-bold text-white mb-2">Email Verified!</h2>
        <p className="text-surface-400 text-sm mb-6">
          Your email has been verified successfully. You can now sign in to your account.
        </p>
        <Link to="/login" className="btn-primary w-full py-3 justify-center">
          Sign In
        </Link>
      </div>
    )
  }

  return (
    <div className="card text-center">
      <div className="w-16 h-16 bg-red-500/20 border border-red-500/30 rounded-full flex items-center justify-center mx-auto mb-4">
        <AlertCircle className="w-8 h-8 text-red-400" />
      </div>
      <h2 className="text-xl font-bold text-white mb-2">Verification Failed</h2>
      <p className="text-surface-400 text-sm mb-6">
        The verification link is invalid or has already been used.
      </p>
      <Link to="/login" className="btn-secondary w-full py-3 justify-center">
        Back to Sign In
      </Link>
    </div>
  )
}
