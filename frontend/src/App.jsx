import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { ProviderContextProvider } from './context/ProviderContext'
import { Toaster } from 'react-hot-toast'
import { AnimatePresence } from 'framer-motion'
import Navbar from './components/layout/Navbar'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import Analyze from './pages/Analyze'
import Compare from './pages/Compare'
import Admin from './pages/Admin'
import About from './pages/About'
import History from './pages/History'
import ReportDetail from './pages/ReportDetail'
import { useAuth } from './context/AuthContext'

function ProtectedRoute({ children, roles }) {
  const { isAuthenticated, user, isLoading } = useAuth()
  if (isLoading) return <div>Loading...</div>
  if (!isAuthenticated) return <Navigate to="/login" replace />
  if (roles && !roles.includes(user?.role)) return <Navigate to="/analyze" replace />
  return children
}

function AppRoutes() {
  return (
    <AnimatePresence mode="wait">
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/analyze" element={<ProtectedRoute><Analyze /></ProtectedRoute>} />
        <Route path="/history" element={<ProtectedRoute><History /></ProtectedRoute>} />
        <Route path="/history/:id" element={<ProtectedRoute><ReportDetail /></ProtectedRoute>} />
        <Route path="/compare" element={<ProtectedRoute roles={['recruiter','admin']}><Compare /></ProtectedRoute>} />
        <Route path="/admin" element={<ProtectedRoute roles={['recruiter','admin']}><Admin /></ProtectedRoute>} />
        <Route path="/about" element={<About />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AnimatePresence>
  )
}

function AppShell() {
  const location = useLocation()
  const { isAuthenticated } = useAuth()
  const authPage = location.pathname === '/login' || location.pathname === '/register'
  return (
    <div className={`app-shell min-h-screen text-white ${isAuthenticated && !authPage && !['/', '/about'].includes(location.pathname) ? 'md:pl-64' : ''}`}>
      {!authPage && <Navbar />}
      <main><AppRoutes /></main>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ProviderContextProvider>
          <AppShell />
          <Toaster position="top-right" toastOptions={{ style: { background: '#0f0f2e', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' } }} />
        </ProviderContextProvider>
      </AuthProvider>
    </BrowserRouter>
  )
}
