import { Outlet } from 'react-router-dom'
import { useEffect } from 'react'

import Footer from '../components/layout/Footer'
import Header from '../components/layout/Header'
import styles from './SiteShell.module.css'
import { useAsyncResource } from '../hooks/useAsyncResource'
import { defaultSettings, settingsService } from '../services/settings'

export default function SiteShell({ navigationItems, onLogout }) {
  const resource = useAsyncResource(settingsService.get)
  useEffect(() => {
    window.addEventListener('cms-settings-updated', resource.retry)
    return () => window.removeEventListener('cms-settings-updated', resource.retry)
  }, [resource.retry])
  const settings = resource.data || defaultSettings
  return <div className={styles.shell}><Header navigationItems={navigationItems} onLogout={onLogout} settings={settings} /><main className={styles.main}><Outlet context={settings} /></main><Footer settings={settings} /></div>
}
