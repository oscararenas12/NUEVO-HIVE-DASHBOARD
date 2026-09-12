import { vi } from 'vitest'
import { render, screen, waitFor } from '../test-utils'

vi.mock('recharts', () => import('../__mocks__/recharts'))
vi.mock('@/api/dashboard', () => ({
  getOverview: vi.fn().mockResolvedValue({
    stats: { total_revenue: 847.50, total_vends: 312, avg_price: 2.72, active_devices: 2, revenue_change: 12.5, vends_change: 8.3, avg_price_change: -1.2, devices_change: 0 },
    daily_revenue: [{ date: '2026-09-01', revenue: 42.50, vends: 17 }],
    recent_transactions: [{ item_ref: '1', device: 'VK200044724', item_date: '2026-09-11T16:19:45', amount: 2.50, slot_code: '0B06', payment_type: 'Credit (EMV Contactless)', settle_status: 'SETTLED' }],
  }),
  getDevices: vi.fn().mockResolvedValue({
    devices: [
      { serial_num: 'VK200044724', location: 'South Gate, CA 90280', revenue: 523.50, vends: 195, avg_price: 2.68, top_slot: '0B06', revenue_share: 61.8 },
    ],
  }),
}))

import Overview from '@/pages/Overview'

describe('Overview', () => {
  it('renders the page title', async () => {
    render(<Overview />)
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /overview/i })).toBeInTheDocument()
    })
  })

  it('renders stat cards with mock data', async () => {
    render(<Overview />)
    await waitFor(() => {
      expect(screen.getByText('$847.50')).toBeInTheDocument()
      expect(screen.getByText('312')).toBeInTheDocument()
    })
  })

  it('renders the revenue chart', async () => {
    render(<Overview />)
    await waitFor(() => {
      expect(screen.getByText('Daily Revenue')).toBeInTheDocument()
    })
  })

  it('renders the recent transactions table', async () => {
    render(<Overview />)
    await waitFor(() => {
      expect(screen.getByText('Recent Transactions')).toBeInTheDocument()
    })
  })
})
