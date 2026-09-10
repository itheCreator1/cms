import { Navigate, Route, Routes } from 'react-router-dom'

import AuthLayout from './layouts/AuthLayout'
import DashboardLayout from './layouts/DashboardLayout'
import PublicLayout from './layouts/PublicLayout'
import Login from './pages/auth/Login'
import SystemAccess from './pages/auth/SystemAccess'
import DashboardHome from './pages/dashboard/DashboardHome'
import AnnouncementsPage from './pages/public/AnnouncementsPage'
import ArticlePage from './pages/public/ArticlePage'
import Home from './pages/public/Home'
import PageView from './pages/public/PageView'
import ProtectedRoute from './routes/ProtectedRoute'

export default function App() {
  return (
    <Routes>
      <Route element={<PublicLayout />}>
        <Route index element={<Home />} />
        <Route path="articles/:slug" element={<ArticlePage />} />
        <Route path="announcements" element={<AnnouncementsPage />} />
        <Route path="pages/:slug" element={<PageView />} />
      </Route>
      <Route element={<AuthLayout />}>
        <Route path="login" element={<Login />} />
        <Route path="system-access" element={<SystemAccess />} />
      </Route>
      <Route element={<ProtectedRoute minimumRole="publisher" />}>
        <Route element={<DashboardLayout />}>
          <Route path="dashboard/*" element={<DashboardHome />} />
        </Route>
      </Route>
      <Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}
