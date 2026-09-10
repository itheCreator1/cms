import { useAuth } from '../context/AuthContext'
import SiteShell from './SiteShell'

export default function DashboardLayout() {
  const { logout } = useAuth()
  return <SiteShell navigationItems={[{ to: '/', label: 'Home' }, { to: '/announcements', label: 'Announcements' }, { to: '/dashboard', label: 'Dashboard' }]} onLogout={logout} />
}
