import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '../test-utils'

vi.mock('recharts', () => import('../__mocks__/recharts'))

import { WeeklyRevenueChart, MonthlyRevenueChart, HourlyPatternChart, DayOfWeekChart } from '@/components/TrendCharts'
import type { WeeklyTrend, MonthlyTrend, HourlyPattern, DayOfWeekPattern } from '@/api/dashboard'

const weekly: WeeklyTrend[] = [
  { week_start: '2026-08-31', revenue: 230.00, vends: 85 },
  { week_start: '2026-09-07', revenue: 218.50, vends: 81 },
]

const monthly: MonthlyTrend[] = [
  { month: '2026-07', revenue: 812.00, vends: 301 },
  { month: '2026-08', revenue: 847.50, vends: 312 },
]

const hourly: HourlyPattern[] = [
  { hour: 0, avg_vends: 0.1, avg_revenue: 0.25 },
  { hour: 12, avg_vends: 3.5, avg_revenue: 9.10 },
]

const dayOfWeek: DayOfWeekPattern[] = [
  { day: 1, day_name: 'Monday', avg_vends: 12.5, avg_revenue: 32.50 },
  { day: 5, day_name: 'Friday', avg_vends: 15.2, avg_revenue: 39.50 },
]

describe('TrendCharts', () => {
  describe('WeeklyRevenueChart', () => {
    it('renders the title', () => {
      render(<WeeklyRevenueChart data={weekly} />)
      expect(screen.getByText('Weekly Revenue')).toBeInTheDocument()
    })

    it('renders inside a card', () => {
      render(<WeeklyRevenueChart data={weekly} />)
      expect(document.querySelector('[data-slot="card"]')).toBeInTheDocument()
    })
  })

  describe('MonthlyRevenueChart', () => {
    it('renders the title', () => {
      render(<MonthlyRevenueChart data={monthly} />)
      expect(screen.getByText('Monthly Revenue')).toBeInTheDocument()
    })
  })

  describe('HourlyPatternChart', () => {
    it('renders the title', () => {
      render(<HourlyPatternChart data={hourly} />)
      expect(screen.getByText('Hourly Pattern')).toBeInTheDocument()
    })
  })

  describe('DayOfWeekChart', () => {
    it('renders the title', () => {
      render(<DayOfWeekChart data={dayOfWeek} />)
      expect(screen.getByText('Day of Week')).toBeInTheDocument()
    })
  })
})
