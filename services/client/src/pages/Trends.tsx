import { useState, useEffect } from 'react'
import { getTrends } from '@/api/dashboard'
import type { TrendsResponse } from '@/api/dashboard'
import { WeeklyRevenueChart, MonthlyRevenueChart, HourlyPatternChart, DayOfWeekChart } from '@/components/TrendCharts'

function Trends() {
  const [data, setData] = useState<TrendsResponse | null>(null)

  useEffect(() => {
    getTrends().then(setData)
  }, [])

  if (!data) return null

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-white">Trends</h1>
        <p className="mt-1 text-sm text-gray-500">Weekly, monthly, and hourly patterns</p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <WeeklyRevenueChart data={data.weekly} />
        <MonthlyRevenueChart data={data.monthly} />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <HourlyPatternChart data={data.hourly} />
        <DayOfWeekChart data={data.day_of_week} />
      </div>
    </div>
  )
}

export default Trends
