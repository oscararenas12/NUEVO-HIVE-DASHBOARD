import { describe, it, expect } from 'vitest'
import { render, screen } from '../test-utils'
import SlotMap from '@/components/SlotMap'
import type { SlotPerformanceData } from '@/api/dashboard'

const slots: SlotPerformanceData[] = [
  { slot_code: '0A02', device: 'VK200044724', revenue: 85.00, vends: 34, avg_price: 2.50, last_vend: '2026-09-11T16:19:45' },
  { slot_code: '0B06', device: 'VK200044724', revenue: 95.00, vends: 38, avg_price: 2.50, last_vend: '2026-09-11T16:19:45' },
  { slot_code: '0C02', device: 'VK200044724', revenue: 60.00, vends: 20, avg_price: 3.00, last_vend: '2026-09-10T17:20:08' },
  { slot_code: '0E06', device: 'VK200044724', revenue: 28.00, vends: 14, avg_price: 2.00, last_vend: '2026-09-08T10:15:33' },
]

describe('SlotMap', () => {
  it('renders the title', () => {
    render(<SlotMap slots={slots} device="VK200044724" />)
    expect(screen.getByText('Slot Map')).toBeInTheDocument()
  })

  it('renders slot codes from the data', () => {
    render(<SlotMap slots={slots} device="VK200044724" />)
    expect(screen.getByText('0A02')).toBeInTheDocument()
    expect(screen.getByText('0B06')).toBeInTheDocument()
  })

  it('renders a grid with correct dimensions', () => {
    render(<SlotMap slots={slots} device="VK200044724" />)
    const grid = document.querySelector('[data-testid="slot-grid"]')
    expect(grid).toBeInTheDocument()
  })

  it('shows revenue values for populated slots', () => {
    render(<SlotMap slots={slots} device="VK200044724" />)
    expect(screen.getByText('$95.00')).toBeInTheDocument()
    expect(screen.getByText('$85.00')).toBeInTheDocument()
  })

  it('renders inside a card', () => {
    render(<SlotMap slots={slots} device="VK200044724" />)
    expect(document.querySelector('[data-slot="card"]')).toBeInTheDocument()
  })
})
