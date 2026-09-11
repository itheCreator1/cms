import { Navigate, Route, Routes } from 'react-router-dom'

import AuthLayout from './layouts/AuthLayout'
import DashboardLayout from './layouts/DashboardLayout'
import PublicLayout from './layouts/PublicLayout'
import Login from './pages/auth/Login'
import SystemAccess from './pages/auth/SystemAccess'
import DashboardHome from './pages/dashboard/DashboardHome'
import ArticleEditor from './pages/dashboard/ArticleEditor'
import ArticleList from './pages/dashboard/ArticleList'
import AnnouncementEditor from './pages/dashboard/AnnouncementEditor'
import AnnouncementList from './pages/dashboard/AnnouncementList'
import PageEditor from './pages/dashboard/PageEditor'
import PageList from './pages/dashboard/PageList'
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
          <Route path="dashboard" element={<DashboardHome />} />
          <Route path="dashboard/articles" element={<ArticleList />} />
          <Route path="dashboard/articles/new" element={<ArticleEditor />} />
          <Route path="dashboard/articles/:id/edit" element={<ArticleEditor />} />
          <Route path="dashboard/announcements" element={<AnnouncementList />} />
          <Route path="dashboard/announcements/new" element={<AnnouncementEditor />} />
          <Route path="dashboard/announcements/:id/edit" element={<AnnouncementEditor />} />
          <Route element={<ProtectedRoute minimumRole="admin" />}>
            <Route path="dashboard/pages" element={<PageList />} />
            <Route path="dashboard/pages/new" element={<PageEditor />} />
            <Route path="dashboard/pages/:id/edit" element={<PageEditor />} />
          </Route>
          <Route path="dashboard/*" element={<Navigate to="/dashboard" replace />} />
        </Route>
      </Route>
      <Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}
