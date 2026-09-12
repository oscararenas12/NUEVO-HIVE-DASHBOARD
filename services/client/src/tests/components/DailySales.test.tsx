import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '../test-utils'

vi.mock('recharts', () => import('../__mocks__/recharts'))

import DailySales from '@/components/DailySales'
import type { DailyRevenue } from '@/api/dashboard'

const data: DailyRevenue[] = [
  { date: '2026-09-01', revenue: 42.50, vends: 17 },
  { date: '2026-09-02', revenue: 38.00, vends: 14 },
]

describe('DailySales', () => {
  it('renders the chart title', () => {
    render(<DailySales data={data} />)
    expect(screen.getByText('Daily Sales Trend')).toBeInTheDocument()
  })

  it('renders inside a card', () => {
    render(<DailySales data={data} />)
    expect(document.querySelector('[data-slot="card"]')).toBeInTheDocument()
  })

  it('renders the recharts container', () => {
    render(<DailySales data={data} />)
    expect(screen.getByTestId('mock-responsive-container')).toBeInTheDocument()
  })
})
