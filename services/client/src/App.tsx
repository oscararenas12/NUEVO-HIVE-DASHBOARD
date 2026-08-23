import { Routes, Route } from 'react-router-dom'
import Layout from '@/components/Layout'
import Overview from '@/pages/Overview'
import SlotPerformance from '@/pages/SlotPerformance'
import Trends from '@/pages/Trends'
import Login from '@/pages/Login'

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Overview />} />
        <Route path="/slots" element={<SlotPerformance />} />
        <Route path="/trends" element={<Trends />} />
      </Route>
      <Route path="/login" element={<Login />} />
    </Routes>
  )
}

export default App
