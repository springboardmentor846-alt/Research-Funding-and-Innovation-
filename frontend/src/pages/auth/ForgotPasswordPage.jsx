import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Mail, Loader2, ArrowLeft, CheckCircle } from 'lucide-react'
import { authService } from '@/services/authService'
import toast from 'react-hot-toast'

const schema = z.object({
  email: z.string().email('Enter a valid email address'),
})

export default function ForgotPasswordPage() {
  const [sent, setSent] = useState(false)

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm({
    resolver: zodResolver(schema),
  })

  const onSubmit = async ({ email }) => {
    try {
      await authService.forgotPassword(email)
      setSent(true)
    } catch {
      // Always show success to prevent enumeration
      setSent(true)
    }
  }

  if (sent) {
    return (
      <div className="card text-center">
        <div className="w-16 h-16 bg-brand-500/20 border border-brand-500/30 rounded-full flex items-center justify-center mx-auto mb-4">
          <CheckCircle className="w-8 h-8 text-brand-400" />
        </div>
        <h2 className="text-xl font-bold text-white mb-2">Check your inbox</h2>
        <p className="text-surface-400 text-sm mb-6">
          If that email is registered with RFIP, you'll receive a password reset link within a few minutes.
        </p>
        <Link to="/login" className="btn-primary w-full py-3 justify-center">
          <ArrowLeft className="w-4 h-4" /> Back to Sign In
        </Link>
      </div>
    )
  }

  return (
    <div className="card">
      <div className="text-center mb-8">
        <div className="w-14 h-14 bg-gradient-to-br from-brand-500 to-accent-500 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-glow-brand">
          <Mail className="w-7 h-7 text-white" />
        </div>
        <h1 className="text-2xl font-bold text-white">Forgot password?</h1>
        <p className="text-surface-400 text-sm mt-1">
          Enter your email and we'll send you a reset link.
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-5">
        <div>
          <label htmlFor="forgot-email" className="form-label">Email address</label>
          <input
            id="forgot-email"
            type="email"
            autoComplete="email"
            placeholder="you@example.com"
            className={`input-field ${errors.email ? 'input-error' : ''}`}
            {...register('email')}
          />
          {errors.email && <p className="error-text">{errors.email.message}</p>}
        </div>

        <button
          id="forgot-submit"
          type="submit"
          disabled={isSubmitting}
          className="btn-primary w-full py-3"
        >
          {isSubmitting
            ? <><Loader2 className="w-4 h-4 animate-spin" /> Sending…</>
            : <><Mail className="w-4 h-4" /> Send Reset Link</>
          }
        </button>
      </form>

      <div className="mt-6 text-center">
        <Link
          to="/login"
          className="inline-flex items-center gap-1.5 text-sm text-surface-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Sign In
        </Link>
      </div>
    </div>
  )
}
