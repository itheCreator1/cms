import { NavLink, Outlet } from 'react-router-dom'

export default function Layout() {
  return (
    <div className="site-shell">
      <header>
        <a className="brand" href="/">CMS</a>
        <nav aria-label="Primary navigation">
          <NavLink to="/">Home</NavLink>
          <NavLink to="/announcements">Announcements</NavLink>
          <NavLink to="/login">Login</NavLink>
        </nav>
      </header>
      <main><Outlet /></main>
      <footer>Milestone 1 project skeleton</footer>
    </div>
  )
}
