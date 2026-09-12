import { vi } from 'vitest'
import { render, screen, waitFor } from '../test-utils'

vi.mock('recharts', () => import('../__mocks__/recharts'))
vi.mock('@/api/dashboard', () => ({
  getTrends: vi.fn().mockResolvedValue({
    weekly: [{ week_start: '2026-09-07', revenue: 218.50, vends: 81 }],
    monthly: [{ month: '2026-08', revenue: 847.50, vends: 312 }],
    hourly: [{ hour: 12, avg_vends: 3.5, avg_revenue: 9.10 }],
    day_of_week: [{ day: 1, day_name: 'Monday', avg_vends: 12.5, avg_revenue: 32.50 }],
  }),
}))

import Trends from '@/pages/Trends'

describe('Trends', () => {
  it('renders the page title', async () => {
    render(<Trends />)
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /trends/i })).toBeInTheDocument()
    })
  })

  it('renders weekly revenue chart', async () => {
    render(<Trends />)
    await waitFor(() => {
      expect(screen.getByText('Weekly Revenue')).toBeInTheDocument()
    })
  })

  it('renders monthly revenue chart', async () => {
    render(<Trends />)
    await waitFor(() => {
      expect(screen.getByText('Monthly Revenue')).toBeInTheDocument()
    })
  })

  it('renders hourly pattern chart', async () => {
    render(<Trends />)
    await waitFor(() => {
      expect(screen.getByText('Hourly Pattern')).toBeInTheDocument()
    })
  })

  it('renders day of week chart', async () => {
    render(<Trends />)
    await waitFor(() => {
      expect(screen.getByText('Day of Week')).toBeInTheDocument()
    })
  })
})
