import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { authService, adminService } from '../services/api'
import Loading from '../components/Loading'
import ProfileDetail from '../components/ProfileDetail'

const ROLE_DASHBOARDS = {
  researcher: {
    title: 'Researcher Dashboard',
    features: ['Funding recommendations', 'Research trends', 'Publication analytics', 'Patent insights', 'Innovation score'],
  },
  startup_founder: {
    title: 'Startup Dashboard',
    features: ['Funding opportunities', 'Technology opportunities', 'Patent intelligence', 'Commercialization insights'],
  },
  innovation_manager: {
    title: 'Innovation Manager Dashboard',
    features: ['Portfolio analytics', 'Innovation pipeline tracking', 'Technology trend monitoring', 'Funding analytics'],
  },
  admin: {
    title: 'Admin Dashboard',
    features: ['User management', 'Platform analytics', 'Recommendation monitoring', 'System reports'],
  },
}

export default function Dashboard() {
  const [user, setUser] = useState(null)
  const [users, setUsers] = useState([])
  const [selected, setSelected] = useState(null)
  const [profileMsg, setProfileMsg] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    authService.getMe()
      .then((res) => setUser(res.data))
      .catch(() => { authService.logout(); navigate('/login') })
  }, [navigate])

  useEffect(() => {
    if (user && user.role === 'innovation_manager') {
      adminService.listUsers()
        .then((res) => {
          const innovators = res.data.filter(u => u.role === 'researcher' || u.role === 'startup_founder')
          setUsers(innovators)
        })
        .catch(() => setError('Failed to load innovation pipeline'))
    }
  }, [user])

  const viewProfile = async (u) => {
    setSelected(null)
    setProfileMsg('Loading profile…')
    try {
      const res = await adminService.getUserProfile(u.id)
      setSelected({ user: u, profile: res.data })
      setProfileMsg('')
    } catch (err) {
      if (err.response?.status === 404) {
        setSelected({ user: u, profile: null })
        setProfileMsg('')
      } else {
        setProfileMsg('Could not load profile.')
      }
    }
  }

  if (!user) return <Loading message="Loading your dashboard…" />

  const dash = ROLE_DASHBOARDS[user.role] || ROLE_DASHBOARDS.researcher

  if (user.role === 'innovation_manager') {
    const researchersCount = users.filter(u => u.role === 'researcher').length
    const foundersCount = users.filter(u => u.role === 'startup_founder').length

    return (
      <div className="dashboard" style={{ maxWidth: 1200 }}>
        <h1>Innovation Pipeline Tracking</h1>
        {error && <div className="error">{error}</div>}

        <div className="stat-grid">
          <div className="stat-card">
            <span className="stat-num">{users.length}</span>
            Total Monitored Innovators
          </div>
          <div className="stat-card">
            <span className="stat-num">{researchersCount}</span>
            Researchers
          </div>
          <div className="stat-card">
            <span className="stat-num">{foundersCount}</span>
            Startup Founders
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginTop: 24 }}>
          <div className="card">
            <h2>Monitored Innovators</h2>
            <div className="table-wrap">
              <table className="user-table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Type</th>
                    <th>Organization</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((u) => (
                    <tr key={u.id}>
                      <td><strong>{u.full_name}</strong><br/><span className="muted" style={{ fontSize: 12 }}>{u.email}</span></td>
                      <td>
                        <span className="role-badge" style={u.role === 'startup_founder'
                          ? { background: 'var(--info-soft)', color: 'var(--info)' } : {}}>
                          {u.role === 'researcher' ? 'Researcher' : 'Founder'}
                        </span>
                      </td>
                      <td>{u.organization || '—'}</td>
                      <td>
                        <button className="mini-view" onClick={() => viewProfile(u)}>
                          View Portfolio
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div>
            {profileMsg && <div className="card"><p className="muted">{profileMsg}</p></div>}
            {selected && (
              <div className="card">
                <h2>{selected.user.full_name}'s Portfolio</h2>
                <p className="muted">
                  {selected.user.role === 'researcher' ? 'Researcher' : 'Startup Founder'} · {selected.user.email}
                </p>
                {selected.profile ? (
                  <ProfileDetail p={selected.profile} />
                ) : (
                  <p className="muted" style={{ marginTop: 16 }}>This user has not created a research profile yet.</p>
                )}
              </div>
            )}
            {!selected && !profileMsg && (
              <div className="card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: 200 }}>
                <p className="muted">Select an innovator from the list to inspect their research profile.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    )
  }

  const isBaseUser = user.role === 'researcher' || user.role === 'startup_founder'

  return (
    <div className="dashboard">
      <div className="card">
        <h1>Welcome, {user.full_name}</h1>
        <p>Email: {user.email}</p>
        <p>Organization: {user.organization || 'Not specified'}</p>
        <p style={{ marginTop: 8 }}>
          <span className="role-badge">{user.role.replace('_', ' ').toUpperCase()}</span>
        </p>
      </div>

      <div className="card">
        <h2>{dash.title}</h2>
        <p className="muted" style={{ marginBottom: 16 }}>Features available for your role:</p>
        <ul style={{ paddingLeft: 20 }}>
          {dash.features.map((f) => {
            const lower = f.toLowerCase()
            let to = null
            if (isBaseUser && lower.includes('funding')) to = '/funding'
            else if (isBaseUser && lower.includes('trend')) to = '/trends'
            return (
              <li key={f} style={{ marginBottom: 6 }}>
                {to ? <Link to={to} className="inline-link">{f} →</Link> : f}
              </li>
            )
          })}
        </ul>
      </div>

      {isBaseUser && (
        <div className="card">
          <h2>Funding Discovery</h2>
          <p className="muted" style={{ marginBottom: 16 }}>
            Personalized funding opportunities matched to your research profile.
          </p>
          <Link to="/funding">
            <button style={{ width: 'auto' }}>View my funding recommendations →</button>
          </Link>
        </div>
      )}
    </div>
  )
}
