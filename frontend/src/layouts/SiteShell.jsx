import { Outlet } from 'react-router-dom'

import Footer from '../components/layout/Footer'
import Header from '../components/layout/Header'
import styles from './SiteShell.module.css'

export default function SiteShell({ navigationItems, onLogout }) {
  return <div className={styles.shell}><Header navigationItems={navigationItems} onLogout={onLogout} /><main className={styles.main}><Outlet /></main><Footer /></div>
}
