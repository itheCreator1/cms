import { Link } from 'react-router-dom'

import typography from '../../components/ui/Typography.module.css'

export default function DashboardHome() {
  return <><h1 className={typography.pageTitle}>Dashboard</h1><p><Link to="/dashboard/articles">Manage articles</Link></p></>
}
