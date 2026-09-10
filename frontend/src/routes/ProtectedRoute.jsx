import { Navigate, Outlet } from 'react-router-dom'

export default function ProtectedRoute() {
  return <Navigate to="/login" replace />
}
