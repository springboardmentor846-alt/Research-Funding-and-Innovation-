import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { authService, extractErrorMessage } from '../services/api'

export default function Register() {
  const [form, setForm] = useState({
    email: '', full_name: '', password: '',
    role: 'researcher', organization: '',
  })
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const res = await authService.register(form)
      localStorage.setItem('token', res.data.access_token)
      localStorage.setItem('user', JSON.stringify(res.data.user))
      navigate(res.data.user.role === 'admin' ? '/admin' : '/dashboard')
    } catch (err) {
      setError(extractErrorMessage(err, 'Registration failed'))
    }
  }


  return (
    <div className="container">
      <h1>Register</h1>
      {error && <div className="error">{error}</div>}
      <form onSubmit={handleSubmit}>
        <input name="full_name" placeholder="Full Name" value={form.full_name}
               onChange={handleChange} required />
        <input name="email" type="email" placeholder="Email" value={form.email}
               onChange={handleChange} required />
        <input name="password" type="password" placeholder="Password (min 6 chars)"
               value={form.password} onChange={handleChange} minLength={6} required />
        <input name="organization" placeholder="Organization (optional)"
               value={form.organization} onChange={handleChange} />
        <select name="role" value={form.role} onChange={handleChange}>
          <option value="researcher">Researcher</option>
          <option value="startup_founder">Startup Founder</option>
        </select>
        <p className="hint">
          Innovation Manager and Administrator roles are assigned by an administrator.
        </p>
        <button type="submit">Create Account</button>
      </form>
      <div className="link">
        Already have an account? <Link to="/login">Login</Link>
      </div>
    </div>
  )
}
