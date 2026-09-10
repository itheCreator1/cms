import { Link, NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

export default function Layout() {
  const { user, logout } = useAuth()

  return (
    <div className="site-shell">
      <header className="site-header">
        <Link className="brand" to="/" aria-label="CMS home">
          <span className="brand__mark">CMS</span>
          <span className="brand__tagline">The daily edition</span>
        </Link>
        <nav aria-label="Primary navigation">
          <NavLink to="/">Home</NavLink>
          <NavLink to="/announcements">Announcements</NavLink>
          {user && <NavLink to="/dashboard">Dashboard</NavLink>}
          {!user && <NavLink to="/login">Login</NavLink>}
          {user && <button type="button" onClick={logout}>Log out</button>}
        </nav>
      </header>
      <main className="site-main"><Outlet /></main>
      <footer className="site-footer">
        <span>CMS</span>
        <span>Independent stories. Shared community.</span>
      </footer>
    </div>
  )
}
