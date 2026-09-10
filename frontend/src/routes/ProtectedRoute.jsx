import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { hasMinimumRole } from '../auth/roles'

export default function ProtectedRoute({ minimumRole = 'publisher' }) {
  const { isRestoring, user } = useAuth()
  const location = useLocation()

  if (isRestoring) return <p role="status">Restoring session…</p>
  if (!user) return <Navigate to="/login" state={{ from: location.pathname }} replace />
  if (!hasMinimumRole(user.role, minimumRole)) return <Navigate to="/" replace />
  return <Outlet />
}
