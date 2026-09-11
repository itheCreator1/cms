import { useAuth } from '../context/AuthContext'
import { hasMinimumRole } from '../auth/roles'
import SiteShell from './SiteShell'

export default function DashboardLayout() {
  const { logout, user } = useAuth()
  const items = [{ to: '/', label: 'Home' }, { to: '/announcements', label: 'Announcements' }, { to: '/dashboard', label: 'Dashboard' }, { to: '/dashboard/articles', label: 'Articles' }, { to: '/dashboard/announcements', label: 'Manage announcements' }]
  if (hasMinimumRole(user?.role, 'admin')) items.push({ to: '/dashboard/pages', label: 'Pages' })
  return <SiteShell navigationItems={items} onLogout={logout} />
}
