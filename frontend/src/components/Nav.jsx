import { Link, useLocation, useNavigate } from 'react-router-dom'
import { authService } from '../services/api'

const LINKS_BY_ROLE = {
  researcher: [
    { to: '/dashboard', label: 'Dashboard' },
    { to: '/profile', label: 'My Profile' },
    { to: '/funding', label: 'Funding' },
    { to: '/trends', label: 'Trends' },
  ],
  startup_founder: [
    { to: '/dashboard', label: 'Dashboard' },
    { to: '/profile', label: 'My Profile' },
    { to: '/funding', label: 'Funding' },
    { to: '/trends', label: 'Trends' },
  ],
  innovation_manager: [
    { to: '/dashboard', label: 'Console' },
  ],
  admin: [
    { to: '/dashboard', label: 'Dashboard' },
    { to: '/admin', label: 'Admin Panel' },
  ],
}

export default function Nav() {
  const { pathname } = useLocation()
  const navigate = useNavigate()
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  const links = LINKS_BY_ROLE[user.role] || LINKS_BY_ROLE.researcher

  const logout = () => { authService.logout(); navigate('/login') }

  return (
    <div className="nav">
      <span className="brand">Innovation Intelligence Platform</span>
      <div className="nav-links">
        {links.map((l) => (
          <Link key={l.to} to={l.to}
                className={pathname === l.to ? 'navlink active' : 'navlink'}>
            {l.label}
          </Link>
        ))}
        {user.full_name && <span className="user-name">{user.full_name}</span>}
        <button className="logout" onClick={logout}>Logout</button>
      </div>
    </div>
  )
}
