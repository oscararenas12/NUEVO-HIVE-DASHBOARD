import { useState, useEffect } from 'react'
import { DollarSign, ShoppingCart, TrendingUp, Monitor } from 'lucide-react'
import { getOverview, getDevices } from '@/api/dashboard'
import type { OverviewResponse, DevicesResponse } from '@/api/dashboard'
import StatCard from '@/components/StatCard'
import RevenueChart from '@/components/RevenueChart'
import DailySales from '@/components/DailySales'
import DeviceBreakdown from '@/components/DeviceBreakdown'
import RecentTransactions from '@/components/RecentTransactions'

function Overview() {
  const [overview, setOverview] = useState<OverviewResponse | null>(null)
  const [devices, setDevices] = useState<DevicesResponse | null>(null)

  useEffect(() => {
    getOverview().then(setOverview)
    getDevices().then(setDevices)
  }, [])

  if (!overview || !devices) return null

  const { stats } = overview

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-white">Overview</h1>
        <p className="mt-1 text-sm text-gray-500">Your vending performance at a glance</p>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Total Revenue" value={`$${stats.total_revenue.toFixed(2)}`} change={stats.revenue_change} icon={DollarSign} />
        <StatCard label="Total Vends" value={String(stats.total_vends)} change={stats.vends_change} icon={ShoppingCart} />
        <StatCard label="Avg Price" value={`$${stats.avg_price.toFixed(2)}`} change={stats.avg_price_change} icon={TrendingUp} />
        <StatCard label="Active Devices" value={String(stats.active_devices)} change={stats.devices_change} icon={Monitor} />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <RevenueChart data={overview.daily_revenue} />
        <DailySales data={overview.daily_revenue} />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <DeviceBreakdown devices={devices.devices} className="lg:col-span-1" />
        <RecentTransactions transactions={overview.recent_transactions} className="lg:col-span-2" />
      </div>
    </div>
  )
}

export default Overview
