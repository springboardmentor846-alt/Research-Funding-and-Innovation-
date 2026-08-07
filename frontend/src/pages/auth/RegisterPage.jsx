import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Eye, EyeOff, FlaskConical, UserPlus, Loader2, CheckCircle } from 'lucide-react'
import { useAuth } from '@/context/AuthContext'
import toast from 'react-hot-toast'

const ROLES = [
  { value: 'researcher',         label: 'Researcher' },
  { value: 'startup_founder',    label: 'Startup Founder' },
  { value: 'innovation_manager', label: 'Innovation Manager' },
]

const schema = z
  .object({
    full_name:       z.string().min(2, 'Name must be at least 2 characters'),
    email:           z.string().email('Enter a valid email address'),
    role:            z.enum(['researcher', 'startup_founder', 'innovation_manager']),
    password:        z
      .string()
      .min(8, 'At least 8 characters')
      .regex(/[A-Z]/, 'Must contain an uppercase letter')
      .regex(/[a-z]/, 'Must contain a lowercase letter')
      .regex(/[0-9]/, 'Must contain a number')
      .regex(/[^A-Za-z0-9]/, 'Must contain a special character'),
    confirm_password: z.string(),
  })
  .refine((d) => d.password === d.confirm_password, {
    message: 'Passwords do not match',
    path: ['confirm_password'],
  })

const strength = (pwd) => {
  let s = 0
  if (pwd.length >= 8) s++
  if (/[A-Z]/.test(pwd)) s++
  if (/[a-z]/.test(pwd)) s++
  if (/[0-9]/.test(pwd)) s++
  if (/[^A-Za-z0-9]/.test(pwd)) s++
  return s
}

const strengthLabel = ['', 'Very weak', 'Weak', 'Fair', 'Good', 'Strong']
const strengthColor = ['', 'bg-red-500', 'bg-orange-500', 'bg-yellow-500', 'bg-green-500', 'bg-emerald-500']

export default function RegisterPage() {
  const { register: authRegister } = useAuth()
  const navigate = useNavigate()
  const [showPwd, setShowPwd]   = useState(false)
  const [showCPwd, setShowCPwd] = useState(false)
  const [success, setSuccess]   = useState(false)
  const [pwdValue, setPwdValue]  = useState('')

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm({
    resolver: zodResolver(schema),
    defaultValues: { role: 'researcher' },
  })

  const onSubmit = async (data) => {
    try {
      await authRegister(data)
      setSuccess(true)
      toast.success('Account created! Check your email to verify.')
    } catch (err) {
      const msg = err?.response?.data?.detail || 'Registration failed. Please try again.'
      toast.error(msg)
    }
  }

  if (success) {
    return (
      <div className="card text-center">
        <div className="w-16 h-16 bg-emerald-500/20 border border-emerald-500/30 rounded-full flex items-center justify-center mx-auto mb-4">
          <CheckCircle className="w-8 h-8 text-emerald-400" />
        </div>
        <h2 className="text-xl font-bold text-white mb-2">Account Created!</h2>
        <p className="text-surface-400 text-sm mb-6">
          We've sent a verification link to your email. Please check your inbox and verify your account before signing in.
        </p>
        <Link to="/login" className="btn-primary w-full py-3 justify-center">
          Go to Sign In
        </Link>
      </div>
    )
  }

  const s = strength(pwdValue)

  return (
    <div className="card">
      {/* Header */}
      <div className="text-center mb-6">
        <div className="w-14 h-14 bg-gradient-to-br from-brand-500 to-accent-500 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-glow-brand">
          <FlaskConical className="w-7 h-7 text-white" />
        </div>
        <h1 className="text-2xl font-bold text-white">Create your account</h1>
        <p className="text-surface-400 text-sm mt-1">Join the RFIP innovation platform</p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-4">
        {/* Full name */}
        <div>
          <label htmlFor="reg-name" className="form-label">Full name</label>
          <input
            id="reg-name"
            type="text"
            autoComplete="name"
            placeholder="Dr. Jane Smith"
            className={`input-field ${errors.full_name ? 'input-error' : ''}`}
            {...register('full_name')}
          />
          {errors.full_name && <p className="error-text">{errors.full_name.message}</p>}
        </div>

        {/* Email */}
        <div>
          <label htmlFor="reg-email" className="form-label">Email address</label>
          <input
            id="reg-email"
            type="email"
            autoComplete="email"
            placeholder="you@example.com"
            className={`input-field ${errors.email ? 'input-error' : ''}`}
            {...register('email')}
          />
          {errors.email && <p className="error-text">{errors.email.message}</p>}
        </div>

        {/* Role */}
        <div>
          <label htmlFor="reg-role" className="form-label">I am a…</label>
          <select
            id="reg-role"
            className="input-field"
            {...register('role')}
          >
            {ROLES.map(({ value, label }) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
        </div>

        {/* Password */}
        <div>
          <label htmlFor="reg-password" className="form-label">Password</label>
          <div className="relative">
            <input
              id="reg-password"
              type={showPwd ? 'text' : 'password'}
              autoComplete="new-password"
              placeholder="••••••••"
              className={`input-field pr-11 ${errors.password ? 'input-error' : ''}`}
              {...register('password', {
                onChange: (e) => setPwdValue(e.target.value),
              })}
            />
            <button
              type="button"
              onClick={() => setShowPwd((s) => !s)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-surface-400 hover:text-white transition-colors"
            >
              {showPwd ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
          {/* Strength bar */}
          {pwdValue && (
            <div className="mt-2 space-y-1">
              <div className="flex gap-1">
                {[1, 2, 3, 4, 5].map((i) => (
                  <div
                    key={i}
                    className={`h-1 flex-1 rounded-full transition-all duration-300 ${
                      i <= s ? strengthColor[s] : 'bg-white/10'
                    }`}
                  />
                ))}
              </div>
              <p className="text-xs text-surface-400">{strengthLabel[s]}</p>
            </div>
          )}
          {errors.password && <p className="error-text">{errors.password.message}</p>}
        </div>

        {/* Confirm password */}
        <div>
          <label htmlFor="reg-confirm" className="form-label">Confirm password</label>
          <div className="relative">
            <input
              id="reg-confirm"
              type={showCPwd ? 'text' : 'password'}
              autoComplete="new-password"
              placeholder="••••••••"
              className={`input-field pr-11 ${errors.confirm_password ? 'input-error' : ''}`}
              {...register('confirm_password')}
            />
            <button
              type="button"
              onClick={() => setShowCPwd((s) => !s)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-surface-400 hover:text-white transition-colors"
            >
              {showCPwd ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
          {errors.confirm_password && (
            <p className="error-text">{errors.confirm_password.message}</p>
          )}
        </div>

        <button
          id="register-submit"
          type="submit"
          disabled={isSubmitting}
          className="btn-primary w-full py-3 mt-2"
        >
          {isSubmitting
            ? <><Loader2 className="w-4 h-4 animate-spin" /> Creating account…</>
            : <><UserPlus className="w-4 h-4" /> Create Account</>
          }
        </button>
      </form>

      <div className="divider mt-6">
        <span>Already have an account?</span>
      </div>

      <Link to="/login" className="btn-secondary w-full text-center mt-4 py-3">
        Sign in
      </Link>
    </div>
  )
}
