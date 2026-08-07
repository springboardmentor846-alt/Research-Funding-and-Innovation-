import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  Users, Search, Shield, ArrowLeft, CheckCircle2,
  XCircle, UserCheck, ShieldAlert, Edit2, Mail
} from 'lucide-react'
import { reportsNotificationsService } from '@/services/reportsNotificationsService'
import toast from 'react-hot-toast'

const ROLE_OPTIONS = [
  { value: 'researcher', label: 'Researcher' },
  { value: 'startup_founder', label: 'Startup Founder' },
  { value: 'innovation_manager', label: 'Innovation Manager' },
  { value: 'administrator', label: 'Administrator' },
]

export default function UserManagementPage() {
  const [users, setUsers] = useState([])
  const [q, setQ] = useState('')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchUsers()
  }, [])

  const fetchUsers = async () => {
    try {
      setIsLoading(true)
      const data = await reportsNotificationsService.getAdminUsers()
      setUsers(data)
    } catch (err) {
      toast.error('Failed to load registered users.')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleToggleStatus = async (user) => {
    try {
      const updated = await reportsNotificationsService.updateUserStatus(user.id, {
        is_active: !user.is_active,
      })
      toast.success(`User ${user.full_name} status updated to ${updated.is_active ? 'Active' : 'Disabled'}`)
      fetchUsers()
    } catch (err) {
      toast.error('Failed to update user status.')
    }
  }

  const handleChangeRole = async (user, newRole) => {
    try {
      const updated = await reportsNotificationsService.updateUserStatus(user.id, {
        role: newRole,
      })
      toast.success(`User ${user.full_name} role updated to ${updated.role}`)
      fetchUsers()
    } catch (err) {
      toast.error('Failed to update user role.')
    }
  }

  const filteredUsers = users.filter((u) => {
    if (!q.trim()) return true
    const term = q.toLowerCase()
    return (
      u.full_name.toLowerCase().includes(term) ||
      u.email.toLowerCase().includes(term) ||
      (u.organization && u.organization.toLowerCase().includes(term))
    )
  })

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* ── Navigation & Header ── */}
      <div className="space-y-4">
        <Link
          to="/admin"
          className="inline-flex items-center gap-2 text-xs font-semibold text-surface-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Admin Control Center
        </Link>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-brand-400 font-semibold text-xs tracking-wider uppercase mb-1">
              <Users className="w-4 h-4" /> User Administration & Access Control
            </div>
            <h1 className="text-2xl md:text-3xl font-extrabold text-white">Platform User Management</h1>
            <p className="text-surface-400 text-sm mt-1">
              Manage platform user accounts, assign user roles, verify credentials, and enable/disable account access.
            </p>
          </div>
        </div>
      </div>

      {/* ── Search Bar ── */}
      <div className="glass p-4 rounded-2xl border border-white/10 flex items-center gap-3">
        <Search className="w-4 h-4 text-surface-400 ml-2" />
        <input
          type="text"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search by full name, email address, or organization..."
          className="w-full bg-transparent text-xs text-white placeholder-surface-500 focus:outline-none"
        />
      </div>

      {/* ── Users Table ── */}
      {isLoading ? (
        <div className="flex flex-col items-center justify-center min-h-[40vh] gap-3">
          <div className="w-10 h-10 rounded-full border-3 border-brand-500 border-t-transparent animate-spin" />
          <p className="text-surface-400 text-xs animate-pulse">Loading registered users...</p>
        </div>
      ) : filteredUsers.length === 0 ? (
        <div className="glass p-12 rounded-2xl border border-white/10 text-center space-y-3">
          <Users className="w-12 h-12 text-surface-500 mx-auto" />
          <h3 className="text-lg font-bold text-white">No Users Found</h3>
          <p className="text-surface-400 text-xs">No users matched your search criteria.</p>
        </div>
      ) : (
        <div className="glass rounded-2xl border border-white/10 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-white/10 bg-surface-900/60 text-surface-400 uppercase tracking-wider font-semibold">
                  <th className="py-3.5 px-4">User</th>
                  <th className="py-3.5 px-4">Role</th>
                  <th className="py-3.5 px-4">Organization</th>
                  <th className="py-3.5 px-4">Status</th>
                  <th className="py-3.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {filteredUsers.map((user) => (
                  <tr key={user.id} className="hover:bg-white/[0.02] transition-colors">
                    {/* User Info */}
                    <td className="py-3.5 px-4">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-full bg-gradient-to-br from-brand-500 to-accent-500 flex items-center justify-center text-white font-bold text-xs flex-shrink-0">
                          {user.full_name?.charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <p className="font-bold text-white text-sm">{user.full_name}</p>
                          <p className="text-surface-400 text-[11px] font-mono">{user.email}</p>
                        </div>
                      </div>
                    </td>

                    {/* Role Select */}
                    <td className="py-3.5 px-4">
                      <select
                        value={user.role}
                        onChange={(e) => handleChangeRole(user, e.target.value)}
                        className="bg-surface-900 border border-white/10 rounded-lg px-2.5 py-1 text-xs text-white focus:border-brand-500 focus:outline-none"
                      >
                        {ROLE_OPTIONS.map((opt) => (
                          <option key={opt.value} value={opt.value}>
                            {opt.label}
                          </option>
                        ))}
                      </select>
                    </td>

                    {/* Organization */}
                    <td className="py-3.5 px-4 text-surface-300">
                      {user.organization || 'Not Specified'}
                    </td>

                    {/* Active Status Badge */}
                    <td className="py-3.5 px-4">
                      <span
                        className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${
                          user.is_active
                            ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                            : 'bg-red-500/10 text-red-400 border-red-500/20'
                        }`}
                      >
                        {user.is_active ? <CheckCircle2 className="w-3 h-3" /> : <XCircle className="w-3 h-3" />}
                        {user.is_active ? 'Active' : 'Disabled'}
                      </span>
                    </td>

                    {/* Actions */}
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={() => handleToggleStatus(user)}
                        className={`btn-secondary text-[11px] py-1 px-3 ${
                          user.is_active ? 'hover:bg-red-500/20 hover:text-red-300' : 'hover:bg-emerald-500/20 hover:text-emerald-300'
                        }`}
                      >
                        {user.is_active ? 'Disable Account' : 'Activate Account'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
