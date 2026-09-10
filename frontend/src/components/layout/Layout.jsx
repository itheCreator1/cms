import { NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

export default function Layout() {
  const { user, logout } = useAuth()

  return (
    <div className="site-shell">
      <header>
        <a className="brand" href="/">CMS</a>
        <nav aria-label="Primary navigation">
          <NavLink to="/">Home</NavLink>
          <NavLink to="/announcements">Announcements</NavLink>
          {user && <NavLink to="/dashboard">Dashboard</NavLink>}
          {!user && <NavLink to="/login">Login</NavLink>}
          {user && <button type="button" onClick={logout}>Log out</button>}
        </nav>
      </header>
      <main><Outlet /></main>
      <footer>Role-based CMS</footer>
    </div>
  )
}
