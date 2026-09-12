import { vi } from 'vitest'
import { render, screen, waitFor } from '../test-utils'

vi.mock('recharts', () => import('../__mocks__/recharts'))
vi.mock('@/api/dashboard', () => ({
  getSlots: vi.fn().mockResolvedValue({
    slots: [
      { slot_code: '0B06', device: 'VK200044724', revenue: 95.00, vends: 38, avg_price: 2.50, last_vend: '2026-09-11T16:19:45' },
      { slot_code: '0A02', device: 'VK200044724', revenue: 85.00, vends: 34, avg_price: 2.50, last_vend: '2026-09-11T16:19:45' },
    ],
    payment_types: [
      { payment_type: 'Credit (EMV Contactless)', revenue: 412.50, vends: 152, percentage: 48.7 },
      { payment_type: 'Cash', revenue: 148.00, vends: 58, percentage: 17.5 },
    ],
  }),
}))

import SlotPerformance from '@/pages/SlotPerformance'

describe('SlotPerformance', () => {
  it('renders the page title', async () => {
    render(<SlotPerformance />)
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /slot performance/i })).toBeInTheDocument()
    })
  })

  it('renders device selector buttons', async () => {
    render(<SlotPerformance />)
    await waitFor(() => {
      expect(screen.getByText('VK200044724')).toBeInTheDocument()
      expect(screen.getByText('VK200044729')).toBeInTheDocument()
    })
  })

  it('renders the slot map', async () => {
    render(<SlotPerformance />)
    await waitFor(() => {
      expect(screen.getByText('Slot Map')).toBeInTheDocument()
    })
  })

  it('renders payment methods', async () => {
    render(<SlotPerformance />)
    await waitFor(() => {
      expect(screen.getByText('Payment Methods')).toBeInTheDocument()
    })
  })
})
