import { Link } from 'react-router-dom'

import Navigation from './Navigation'
import styles from './Header.module.css'

export default function Header({ navigationItems, onLogout }) {
  return (
    <header className={styles.header}>
      <Link className={styles.brand} to="/" aria-label="CMS home">
        <span className={styles.mark}>CMS</span>
        <span className={styles.tagline}>The daily edition</span>
      </Link>
      <Navigation items={navigationItems} onLogout={onLogout} />
    </header>
  )
}
