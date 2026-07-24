import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { adminService, authService } from '../services/api'
import ProfileDetail from '../components/ProfileDetail'

const SUPER_ADMIN_EMAIL = 'aryan@admin.com'

const ROLES = [
  { value: 'researcher', label: 'Researcher' },
  { value: 'startup_founder', label: 'Startup Founder' },
  { value: 'innovation_manager', label: 'Innovation Manager' },
  { value: 'admin', label: 'Administrator' },
]
const ROLES_FOR_ADMIN = ROLES.filter((r) => r.value !== 'admin')
const ROLE_LABEL = Object.fromEntries(ROLES.map((r) => [r.value, r.label]))

export default function AdminPanel() {
  const [users, setUsers] = useState([])
  const [me, setMe] = useState(null)
  const [selected, setSelected] = useState(null)
  const [profileMsg, setProfileMsg] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const loadUsers = () => {
    adminService.listUsers()
      .then((res) => setUsers(res.data))
      .catch((err) => {
        if (err.response?.status === 401) { authService.logout(); navigate('/login') }
        else setError('Failed to load users')
      })
  }

  useEffect(() => {
    authService.getMe().then((res) => setMe(res.data)).catch(() => {})
    loadUsers()
  }, [])   // eslint-disable-line

  const isSuperAdmin = me?.email === SUPER_ADMIN_EMAIL

  const changeRole = async (userId, role) => {
    try {
      await adminService.changeRole(userId, role)
      loadUsers()
    } catch (err) {
      alert(err.response?.data?.detail || 'Could not change role')
    }
  }

  const deleteUser = async (u) => {
    if (!window.confirm(`Delete user "${u.full_name}" (${u.email}) permanently? This cannot be undone.`)) return
    try {
      await adminService.deleteUser(u.id)
      if (selected && selected.user.id === u.id) setSelected(null)
      loadUsers()
    } catch (err) {
      alert(err.response?.data?.detail || 'Could not delete user')
    }
  }

  const viewProfile = async (u) => {
    setSelected(null); setProfileMsg('Loading profile...')
    try {
      const res = await adminService.getUserProfile(u.id)
      setSelected({ user: u, profile: res.data }); setProfileMsg('')
    } catch (err) {
      if (err.response?.status === 404) {
        setSelected({ user: u, profile: null }); setProfileMsg('')
      } else {
        setProfileMsg('Could not load profile')
      }
    }
  }

  const counts = users.reduce((acc, u) => {
    acc[u.role] = (acc[u.role] || 0) + 1
    return acc
  }, {})

  return (
    <div className="dashboard">
        <h1>Platform Administration</h1>
        {error && <div className="error">{error}</div>}

        <div className="stat-grid">
          <div className="stat-card"><span className="stat-num">{users.length}</span>Total Users</div>
          <div className="stat-card"><span className="stat-num">{counts.researcher || 0}</span>Researchers</div>
          <div className="stat-card"><span className="stat-num">{counts.startup_founder || 0}</span>Startup Founders</div>
          <div className="stat-card"><span className="stat-num">{counts.innovation_manager || 0}</span>Innovation Managers</div>
          <div className="stat-card"><span className="stat-num">{counts.admin || 0}</span>Admins</div>
        </div>

        <div className="card">
          <h2>All Users</h2>
          <div className="table-wrap">
            <table className="user-table">
              <thead>
                <tr><th>Name</th><th>Email</th><th>Role</th><th>Organization</th><th colSpan={2}>Actions</th></tr>
              </thead>
              <tbody>
                {users.map((u) => {
                  const isSelf = me && u.id === me.id
                  const targetIsAdmin = u.role === 'admin'
                  const isProtected = targetIsAdmin && !isSuperAdmin
                  const availableRoles = isSuperAdmin ? ROLES : ROLES_FOR_ADMIN

                  return (
                    <tr key={u.id} style={isProtected ? { background: 'rgba(255,200,0,0.05)' } : {}}>
                      <td>
                        {u.full_name}
                        {u.email === SUPER_ADMIN_EMAIL && (
                          <span style={{
                            marginLeft: 6, fontSize: 10, background: '#cca01a',
                            color: '#fff', borderRadius: 4, padding: '1px 5px', verticalAlign: 'middle'
                          }}>SUPER</span>
                        )}
                      </td>
                      <td>{u.email}</td>
                      <td>
                        {isProtected ? (
                          <span className="role-badge" style={{ background: 'var(--warning-soft)', color: 'var(--warning)' }}>
                            🔒 {ROLE_LABEL[u.role]}
                          </span>
                        ) : (
                          <select
                            className="role-select"
                            value={u.role}
                            disabled={isSelf}
                            onChange={(e) => changeRole(u.id, e.target.value)}
                          >
                            {availableRoles.map((r) => {
                              const orig = u.original_role || u.role
                              const isBase = (role) => role === 'researcher' || role === 'startup_founder'
                              const isInvalidBaseChange = isBase(r.value) && isBase(orig) && r.value !== orig
                              return (
                                <option key={r.value} value={r.value} disabled={isInvalidBaseChange}>
                                  {r.label}
                                </option>
                              )
                            })}
                          </select>
                        )}
                      </td>
                      <td>{u.organization || '—'}</td>
                      <td><button className="mini-view" onClick={() => viewProfile(u)}>View Profile</button></td>
                      <td>
                        {isProtected ? (
                          <span style={{ fontSize: 12, color: 'var(--muted)' }}>Protected</span>
                        ) : (
                          <button
                            className="mini-del"
                            disabled={isSelf}
                            onClick={() => deleteUser(u)}
                          >Delete</button>
                        )}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
          {me && (
            <p className="hint">
              {isSuperAdmin
                ? '👑 You are the Super-Admin — you have full control over all accounts including other admins.'
                : '⚠️ As Admin you can manage users and managers. Admin accounts are protected — only the Super-Admin can modify them.'}
            </p>
          )}
        </div>

        {profileMsg && <div className="card"><p className="muted">{profileMsg}</p></div>}
        {selected && (
          <div className="card">
            <h2>{selected.user.full_name} — Research Profile</h2>
            <p className="muted">{ROLE_LABEL[selected.user.role]} · {selected.user.email}</p>
            {selected.profile ? (
              <ProfileDetail p={selected.profile} />
            ) : (
              <p className="muted" style={{ marginTop: 12 }}>This user hasn't created a research profile yet.</p>
            )}
          </div>
        )}
    </div>
  )
}
