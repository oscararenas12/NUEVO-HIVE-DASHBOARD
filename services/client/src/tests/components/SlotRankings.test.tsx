import { describe, it, expect } from 'vitest'
import { render, screen } from '../test-utils'
import SlotRankings from '@/components/SlotRankings'
import type { SlotPerformanceData } from '@/api/dashboard'

const slots: SlotPerformanceData[] = [
  { slot_code: '0B06', device: 'VK200044724', revenue: 95.00, vends: 38, avg_price: 2.50, last_vend: '2026-09-11T16:19:45' },
  { slot_code: '0A02', device: 'VK200044724', revenue: 85.00, vends: 34, avg_price: 2.50, last_vend: '2026-09-11T16:19:45' },
  { slot_code: '0A06', device: 'VK200044724', revenue: 72.00, vends: 24, avg_price: 3.00, last_vend: '2026-09-11T11:08:19' },
  { slot_code: '0D07', device: 'VK200044724', revenue: 66.00, vends: 22, avg_price: 3.00, last_vend: '2026-09-11T15:42:10' },
  { slot_code: '0C02', device: 'VK200044724', revenue: 60.00, vends: 20, avg_price: 3.00, last_vend: '2026-09-10T17:20:08' },
  { slot_code: '0C05', device: 'VK200044724', revenue: 52.50, vends: 21, avg_price: 2.50, last_vend: '2026-09-09T15:33:12' },
  { slot_code: '0B03', device: 'VK200044724', revenue: 45.00, vends: 18, avg_price: 2.50, last_vend: '2026-09-10T14:22:55' },
  { slot_code: '0E03', device: 'VK200044724', revenue: 42.50, vends: 17, avg_price: 2.50, last_vend: '2026-09-11T13:30:21' },
  { slot_code: '0D04', device: 'VK200044724', revenue: 37.50, vends: 15, avg_price: 2.50, last_vend: '2026-09-11T09:45:12' },
  { slot_code: '0E06', device: 'VK200044724', revenue: 28.00, vends: 14, avg_price: 2.00, last_vend: '2026-09-08T10:15:33' },
]

describe('SlotRankings', () => {
  it('renders top performers heading', () => {
    render(<SlotRankings slots={slots} />)
    expect(screen.getByText('Top Performers')).toBeInTheDocument()
  })

  it('renders lowest performers heading', () => {
    render(<SlotRankings slots={slots} />)
    expect(screen.getByText('Lowest Performers')).toBeInTheDocument()
  })

  it('shows the highest revenue slot first in top performers', () => {
    render(<SlotRankings slots={slots} />)
    const topSection = screen.getByText('Top Performers').closest('div')!
    expect(topSection.textContent).toContain('0B06')
    expect(topSection.textContent).toContain('$95.00')
  })

  it('shows the lowest revenue slot in lowest performers', () => {
    render(<SlotRankings slots={slots} />)
    const bottomSection = screen.getByText('Lowest Performers').closest('div')!
    expect(bottomSection.textContent).toContain('0E06')
    expect(bottomSection.textContent).toContain('$28.00')
  })

  it('renders inside a card', () => {
    render(<SlotRankings slots={slots} />)
    expect(document.querySelector('[data-slot="card"]')).toBeInTheDocument()
  })
})
