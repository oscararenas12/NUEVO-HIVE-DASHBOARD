import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from './AuthContext'

function ProtectedRoute() {
  if (!import.meta.env.VITE_API_URL) return <Outlet />
  const { isAuthenticated, isLoading } = useAuth()
  if (isLoading) return null
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return <Outlet />
}

export default ProtectedRoute
