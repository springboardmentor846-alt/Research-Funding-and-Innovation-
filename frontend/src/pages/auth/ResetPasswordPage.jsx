import { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Eye, EyeOff, KeyRound, Loader2, CheckCircle, AlertCircle } from 'lucide-react'
import { authService } from '@/services/authService'
import toast from 'react-hot-toast'

const schema = z
  .object({
    new_password: z
      .string()
      .min(8, 'At least 8 characters')
      .regex(/[A-Z]/, 'Must contain an uppercase letter')
      .regex(/[a-z]/, 'Must contain a lowercase letter')
      .regex(/[0-9]/, 'Must contain a number')
      .regex(/[^A-Za-z0-9]/, 'Must contain a special character'),
    confirm_password: z.string(),
  })
  .refine((d) => d.new_password === d.confirm_password, {
    message: 'Passwords do not match',
    path: ['confirm_password'],
  })

export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const token = searchParams.get('token')

  const [showPwd, setShowPwd]   = useState(false)
  const [showCPwd, setShowCPwd] = useState(false)
  const [success, setSuccess]   = useState(false)

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm({
    resolver: zodResolver(schema),
  })

  if (!token) {
    return (
      <div className="card text-center">
        <div className="w-16 h-16 bg-red-500/20 border border-red-500/30 rounded-full flex items-center justify-center mx-auto mb-4">
          <AlertCircle className="w-8 h-8 text-red-400" />
        </div>
        <h2 className="text-xl font-bold text-white mb-2">Invalid Link</h2>
        <p className="text-surface-400 text-sm mb-6">
          This password reset link is invalid or has expired.
        </p>
        <Link to="/forgot-password" className="btn-primary w-full py-3 justify-center">
          Request a new link
        </Link>
      </div>
    )
  }

  const onSubmit = async ({ new_password, confirm_password }) => {
    try {
      await authService.resetPassword(token, new_password, confirm_password)
      setSuccess(true)
      toast.success('Password reset successfully!')
    } catch (err) {
      const msg = err?.response?.data?.detail || 'Reset failed. The link may have expired.'
      toast.error(msg)
    }
  }

  if (success) {
    return (
      <div className="card text-center">
        <div className="w-16 h-16 bg-emerald-500/20 border border-emerald-500/30 rounded-full flex items-center justify-center mx-auto mb-4">
          <CheckCircle className="w-8 h-8 text-emerald-400" />
        </div>
        <h2 className="text-xl font-bold text-white mb-2">Password Reset!</h2>
        <p className="text-surface-400 text-sm mb-6">
          Your password has been updated successfully. You can now sign in with your new password.
        </p>
        <Link to="/login" className="btn-primary w-full py-3 justify-center">
          Sign In
        </Link>
      </div>
    )
  }

  return (
    <div className="card">
      <div className="text-center mb-8">
        <div className="w-14 h-14 bg-gradient-to-br from-brand-500 to-accent-500 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-glow-brand">
          <KeyRound className="w-7 h-7 text-white" />
        </div>
        <h1 className="text-2xl font-bold text-white">Set new password</h1>
        <p className="text-surface-400 text-sm mt-1">
          Choose a strong password for your account.
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-5">
        {/* New password */}
        <div>
          <label htmlFor="reset-password" className="form-label">New password</label>
          <div className="relative">
            <input
              id="reset-password"
              type={showPwd ? 'text' : 'password'}
              placeholder="••••••••"
              className={`input-field pr-11 ${errors.new_password ? 'input-error' : ''}`}
              {...register('new_password')}
            />
            <button
              type="button"
              onClick={() => setShowPwd((s) => !s)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-surface-400 hover:text-white"
            >
              {showPwd ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
          {errors.new_password && <p className="error-text">{errors.new_password.message}</p>}
        </div>

        {/* Confirm */}
        <div>
          <label htmlFor="reset-confirm" className="form-label">Confirm new password</label>
          <div className="relative">
            <input
              id="reset-confirm"
              type={showCPwd ? 'text' : 'password'}
              placeholder="••••••••"
              className={`input-field pr-11 ${errors.confirm_password ? 'input-error' : ''}`}
              {...register('confirm_password')}
            />
            <button
              type="button"
              onClick={() => setShowCPwd((s) => !s)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-surface-400 hover:text-white"
            >
              {showCPwd ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
          {errors.confirm_password && (
            <p className="error-text">{errors.confirm_password.message}</p>
          )}
        </div>

        <button
          id="reset-submit"
          type="submit"
          disabled={isSubmitting}
          className="btn-primary w-full py-3"
        >
          {isSubmitting
            ? <><Loader2 className="w-4 h-4 animate-spin" /> Resetting…</>
            : <><KeyRound className="w-4 h-4" /> Reset Password</>
          }
        </button>
      </form>
    </div>
  )
}
