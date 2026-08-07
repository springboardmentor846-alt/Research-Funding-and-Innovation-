import { useAuth } from '@/context/AuthContext'

/**
 * Returns true if the current user has one of the given roles
 * or is a superuser.
 *
 * @param {...string} roles - Role strings to check
 * @returns {boolean}
 *
 * @example
 *   const canAdmin = useRole('administrator')
 */
export function useRole(...roles) {
  const { user } = useAuth()
  if (!user) return false
  if (user.is_superuser) return true
  return roles.includes(user.role)
}

/**
 * Returns the current user's role label.
 */
export function useRoleLabel() {
  const { user } = useAuth()
  const labels = {
    researcher:        'Researcher',
    startup_founder:   'Startup Founder',
    innovation_manager:'Innovation Manager',
    administrator:     'Administrator',
  }
  return labels[user?.role] ?? 'Unknown'
}
