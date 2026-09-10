import { useAuth } from '../context/AuthContext'
import SiteShell from './SiteShell'

export default function AuthLayout() {
  const { user, logout } = useAuth()
  const navigationItems = [{ to: '/', label: 'Home' }, { to: '/announcements', label: 'Announcements' }]
  return <SiteShell navigationItems={navigationItems} onLogout={user ? logout : undefined} />
}
