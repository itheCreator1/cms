import { Link } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { hasMinimumRole } from '../../auth/roles'

import typography from '../../components/ui/Typography.module.css'

export default function DashboardHome() {
  const { user } = useAuth()
  return <><h1 className={typography.pageTitle}>Dashboard</h1><p><Link to="/dashboard/articles">Manage articles</Link></p><p><Link to="/dashboard/announcements">Manage announcements</Link></p>{hasMinimumRole(user?.role, 'admin') && <><p><Link to="/dashboard/pages">Manage pages</Link></p><p><Link to="/dashboard/categories">Manage categories</Link></p><p><Link to="/dashboard/tags">Manage tags</Link></p><p><Link to="/dashboard/media">Manage media</Link></p><p><Link to="/dashboard/users">Manage users</Link></p></>}{hasMinimumRole(user?.role, 'superadmin') && <p><Link to="/dashboard/settings">Manage settings</Link></p>}</>
}
