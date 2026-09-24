import { useAuth } from '../context/AuthContext'
import { hasMinimumRole } from '../auth/roles'
import SiteShell from './SiteShell'

export default function DashboardLayout() {
  const { logout, user } = useAuth()
  const items = [{ to: '/', label: 'Home' }, { to: '/announcements', label: 'Announcements' }, { to: '/dashboard', label: 'Dashboard' }, { to: '/dashboard/articles', label: 'Articles' }, { to: '/dashboard/announcements', label: 'Manage announcements' }]
  if (hasMinimumRole(user?.role, 'admin')) items.push(
    { to: '/dashboard/pages', label: 'Pages' },
    { to: '/dashboard/categories', label: 'Categories' },
    { to: '/dashboard/tags', label: 'Tags' },
    { to: '/dashboard/media', label: 'Media' },
    { to: '/dashboard/users', label: 'Users' },
  )
  if (hasMinimumRole(user?.role, 'superadmin')) items.push({ to: '/dashboard/settings', label: 'Settings' })
  return <SiteShell navigationItems={items} onLogout={logout} />
}
