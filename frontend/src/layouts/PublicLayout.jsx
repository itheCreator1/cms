import { useAuth } from '../context/AuthContext'
import { hasMinimumRole } from '../auth/roles'
import SiteShell from './SiteShell'

export default function PublicLayout() {
  const { user, logout } = useAuth()
  const navigationItems = [{ to: '/', label: 'Home' }, { to: '/announcements', label: 'Announcements' }]
  if (user && hasMinimumRole(user.role, 'publisher')) navigationItems.push({ to: '/dashboard', label: 'Dashboard' })
  if (!user) navigationItems.push({ to: '/login', label: 'Login' })
  return <SiteShell navigationItems={navigationItems} onLogout={user ? logout : undefined} />
}
