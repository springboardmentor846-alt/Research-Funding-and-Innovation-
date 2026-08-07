import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { User, Save, Loader2, KeyRound, Building2, Phone, Globe, Linkedin } from 'lucide-react'
import { useAuth } from '@/context/AuthContext'
import { userService } from '@/services/authService'
import toast from 'react-hot-toast'

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

const profileSchema = z.object({
  full_name:    z.string().min(2, 'Name must be at least 2 characters'),
  bio:          z.string().max(2000).optional(),
  organization: z.string().max(255).optional(),
  position:     z.string().max(255).optional(),
  phone_number: z.string().max(50).optional(),
  linkedin_url: z.string().url('Enter a valid URL').optional().or(z.literal('')),
  website_url:  z.string().url('Enter a valid URL').optional().or(z.literal('')),
})

const pwdSchema = z
  .object({
    current_password:     z.string().min(1, 'Current password is required'),
    new_password:         z
      .string()
      .min(8, 'At least 8 characters')
      .regex(/[A-Z]/, 'Must contain uppercase')
      .regex(/[a-z]/, 'Must contain lowercase')
      .regex(/[0-9]/, 'Must contain a number')
      .regex(/[^A-Za-z0-9]/, 'Must contain a special character'),
    confirm_new_password: z.string(),
  })
  .refine((d) => d.new_password === d.confirm_new_password, {
    message: 'Passwords do not match',
    path: ['confirm_new_password'],
  })

function Avatar({ name }) {
  return (
    <div className="w-24 h-24 rounded-2xl bg-gradient-to-br from-brand-500 to-accent-500 flex items-center justify-center text-4xl font-extrabold text-white shadow-glow-brand">
      {name?.charAt(0).toUpperCase()}
    </div>
  )
}

export default function ProfilePage() {
  const { user, updateUser, refreshUser } = useAuth()
  const [activeTab, setActiveTab] = useState('profile')

  // ── Profile form ─────────────────────────────────────────────────────────
  const {
    register: regProfile,
    handleSubmit: handleProfile,
    formState: { errors: profileErrors, isSubmitting: profileSubmitting },
  } = useForm({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      full_name:    user?.full_name    || '',
      bio:          user?.bio          || '',
      organization: user?.organization || '',
      position:     user?.position     || '',
      phone_number: user?.phone_number || '',
      linkedin_url: user?.linkedin_url || '',
      website_url:  user?.website_url  || '',
    },
  })

  const onProfileSubmit = async (data) => {
    try {
      // Remove empty optional strings
      const cleaned = Object.fromEntries(
        Object.entries(data).map(([k, v]) => [k, v === '' ? null : v])
      )
      const updated = await userService.updateProfile(cleaned)
      updateUser(updated)
      toast.success('Profile updated!')
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to update profile.')
    }
  }

  // ── Password form ─────────────────────────────────────────────────────────
  const {
    register: regPwd,
    handleSubmit: handlePwd,
    reset: resetPwd,
    formState: { errors: pwdErrors, isSubmitting: pwdSubmitting },
  } = useForm({ resolver: zodResolver(pwdSchema) })

  const onPwdSubmit = async ({ current_password, new_password, confirm_new_password }) => {
    try {
      await userService.changePassword(current_password, new_password, confirm_new_password)
      toast.success('Password changed successfully!')
      resetPwd()
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to change password.')
    }
  }

  const tabs = [
    { key: 'profile',  label: 'Profile Info' },
    { key: 'password', label: 'Change Password' },
  ]

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header card */}
      <div className="glass p-6 flex flex-col sm:flex-row items-start sm:items-center gap-5">
        <Avatar name={user?.full_name} />
        <div className="flex-1 min-w-0">
          <h1 className="text-2xl font-bold text-white truncate">{user?.full_name}</h1>
          <p className="text-surface-400 text-sm mt-0.5 truncate">{user?.email}</p>
          <div className="flex flex-wrap gap-2 mt-2">
            <span className={`badge ${ROLE_COLORS[user?.role]}`}>
              {ROLE_LABELS[user?.role]}
            </span>
            {user?.is_verified
              ? <span className="badge-green badge">✓ Verified</span>
              : <span className="badge-red badge">Unverified</span>
            }
            {user?.organization && (
              <span className="badge bg-surface-800 text-surface-300 border border-white/5">
                {user.organization}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-white/10">
        {tabs.map(({ key, label }) => (
          <button
            key={key}
            onClick={() => setActiveTab(key)}
            className={`px-5 py-3 text-sm font-medium transition-colors border-b-2 -mb-px ${
              activeTab === key
                ? 'border-brand-500 text-brand-400'
                : 'border-transparent text-surface-400 hover:text-white'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* ── Profile form ── */}
      {activeTab === 'profile' && (
        <form onSubmit={handleProfile(onProfileSubmit)} className="card space-y-5">
          <h2 className="font-semibold text-white flex items-center gap-2">
            <User className="w-4 h-4 text-brand-400" /> Personal Information
          </h2>

          <div className="grid sm:grid-cols-2 gap-4">
            <div>
              <label className="form-label">Full name *</label>
              <input
                id="profile-name"
                className={`input-field ${profileErrors.full_name ? 'input-error' : ''}`}
                {...regProfile('full_name')}
              />
              {profileErrors.full_name && <p className="error-text">{profileErrors.full_name.message}</p>}
            </div>

            <div>
              <label className="form-label">
                <Building2 className="inline w-3.5 h-3.5 mr-1" />Organisation
              </label>
              <input
                id="profile-org"
                placeholder="MIT, Acme Corp…"
                className={`input-field ${profileErrors.organization ? 'input-error' : ''}`}
                {...regProfile('organization')}
              />
            </div>

            <div>
              <label className="form-label">Position / Title</label>
              <input
                id="profile-position"
                placeholder="Senior Researcher"
                className="input-field"
                {...regProfile('position')}
              />
            </div>

            <div>
              <label className="form-label">
                <Phone className="inline w-3.5 h-3.5 mr-1" />Phone number
              </label>
              <input
                id="profile-phone"
                placeholder="+1 555 000 0000"
                className="input-field"
                {...regProfile('phone_number')}
              />
            </div>

            <div>
              <label className="form-label">
                <Linkedin className="inline w-3.5 h-3.5 mr-1" />LinkedIn URL
              </label>
              <input
                id="profile-linkedin"
                placeholder="https://linkedin.com/in/…"
                className={`input-field ${profileErrors.linkedin_url ? 'input-error' : ''}`}
                {...regProfile('linkedin_url')}
              />
              {profileErrors.linkedin_url && <p className="error-text">{profileErrors.linkedin_url.message}</p>}
            </div>

            <div>
              <label className="form-label">
                <Globe className="inline w-3.5 h-3.5 mr-1" />Website URL
              </label>
              <input
                id="profile-website"
                placeholder="https://yourwebsite.com"
                className={`input-field ${profileErrors.website_url ? 'input-error' : ''}`}
                {...regProfile('website_url')}
              />
              {profileErrors.website_url && <p className="error-text">{profileErrors.website_url.message}</p>}
            </div>
          </div>

          <div>
            <label className="form-label">Bio</label>
            <textarea
              id="profile-bio"
              rows={4}
              placeholder="Tell us about your research interests, expertise, and goals…"
              className="input-field resize-none"
              {...regProfile('bio')}
            />
          </div>

          <div className="flex justify-end">
            <button id="profile-save" type="submit" disabled={profileSubmitting} className="btn-primary">
              {profileSubmitting
                ? <><Loader2 className="w-4 h-4 animate-spin" /> Saving…</>
                : <><Save className="w-4 h-4" /> Save Changes</>
              }
            </button>
          </div>
        </form>
      )}

      {/* ── Password form ── */}
      {activeTab === 'password' && (
        <form onSubmit={handlePwd(onPwdSubmit)} className="card space-y-5">
          <h2 className="font-semibold text-white flex items-center gap-2">
            <KeyRound className="w-4 h-4 text-brand-400" /> Change Password
          </h2>

          {[
            { id: 'pwd-current', label: 'Current password',      field: 'current_password',     err: pwdErrors.current_password },
            { id: 'pwd-new',     label: 'New password',           field: 'new_password',          err: pwdErrors.new_password },
            { id: 'pwd-confirm', label: 'Confirm new password',   field: 'confirm_new_password',  err: pwdErrors.confirm_new_password },
          ].map(({ id, label, field, err }) => (
            <div key={field}>
              <label htmlFor={id} className="form-label">{label}</label>
              <input
                id={id}
                type="password"
                className={`input-field ${err ? 'input-error' : ''}`}
                {...regPwd(field)}
              />
              {err && <p className="error-text">{err.message}</p>}
            </div>
          ))}

          <div className="flex justify-end">
            <button id="pwd-save" type="submit" disabled={pwdSubmitting} className="btn-primary">
              {pwdSubmitting
                ? <><Loader2 className="w-4 h-4 animate-spin" /> Updating…</>
                : <><KeyRound className="w-4 h-4" /> Update Password</>
              }
            </button>
          </div>
        </form>
      )}
    </div>
  )
}
