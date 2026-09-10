import { Navigate, Route, Routes } from 'react-router-dom'

import Layout from './components/layout/Layout'
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
      <Route element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="articles/:slug" element={<ArticlePage />} />
        <Route path="announcements" element={<AnnouncementsPage />} />
        <Route path="pages/:slug" element={<PageView />} />
        <Route path="login" element={<Login />} />
        <Route path="system-access" element={<SystemAccess />} />
        <Route element={<ProtectedRoute />}>
          <Route path="dashboard/*" element={<DashboardHome />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}
