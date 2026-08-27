import { Routes, Route } from 'react-router-dom'
import { AuthProvider } from '@/auth/AuthContext'
import ProtectedRoute from '@/auth/ProtectedRoute'
import Layout from '@/components/Layout'
import Overview from '@/pages/Overview'
import SlotPerformance from '@/pages/SlotPerformance'
import Trends from '@/pages/Trends'
import Login from '@/pages/Login'
import Register from '@/pages/Register'

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route element={<ProtectedRoute />}>
          <Route element={<Layout />}>
            <Route path="/" element={<Overview />} />
            <Route path="/slots" element={<SlotPerformance />} />
            <Route path="/trends" element={<Trends />} />
          </Route>
        </Route>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Routes>
    </AuthProvider>
  )
}

export default App
