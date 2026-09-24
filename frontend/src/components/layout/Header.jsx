import { Link } from 'react-router-dom'

import Navigation from './Navigation'
import styles from './Header.module.css'

export default function Header({ navigationItems, onLogout, settings }) {
  return (
    <header className={styles.header}>
      <Link className={styles.brand} to="/" aria-label={`${settings.site_name} home`}>
        <span className={styles.mark}>{settings.site_name}</span>
        <span className={styles.tagline}>{settings.tagline}</span>
      </Link>
      <Navigation items={navigationItems} onLogout={onLogout} />
    </header>
  )
}
