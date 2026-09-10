import { NavLink } from 'react-router-dom'

import Button from '../ui/Button'
import styles from './Navigation.module.css'

export default function Navigation({ items, onLogout }) {
  return (
    <nav className={styles.navigation} aria-label="Primary navigation">
      {items.map((item) => (
        <NavLink key={item.to} to={item.to} className={({ isActive }) => (isActive ? styles.active : undefined)}>
          {item.label}
        </NavLink>
      ))}
      {onLogout && <Button className={styles.logout} onClick={onLogout}>Log out</Button>}
    </nav>
  )
}
