import { describe, it, expect } from 'vitest'
import { render, screen } from '../test-utils'
import DeviceBreakdown from '@/components/DeviceBreakdown'
import type { DeviceStats } from '@/api/dashboard'

const devices: DeviceStats[] = [
  { serial_num: 'VK200044724', location: 'South Gate, CA 90280', revenue: 523.50, vends: 195, avg_price: 2.68, top_slot: '0B06', revenue_share: 61.8 },
  { serial_num: 'VK200044729', location: 'South Gate, CA 90280', revenue: 324.00, vends: 117, avg_price: 2.77, top_slot: '0A02', revenue_share: 38.2 },
]

describe('DeviceBreakdown', () => {
  it('renders both device serial numbers', () => {
    render(<DeviceBreakdown devices={devices} />)
    expect(screen.getByText('VK200044724')).toBeInTheDocument()
    expect(screen.getByText('VK200044729')).toBeInTheDocument()
  })

  it('shows revenue for each device', () => {
    render(<DeviceBreakdown devices={devices} />)
    expect(screen.getByText('$523.50')).toBeInTheDocument()
    expect(screen.getByText('$324.00')).toBeInTheDocument()
  })

  it('shows vend counts', () => {
    render(<DeviceBreakdown devices={devices} />)
    expect(screen.getByText('195 vends')).toBeInTheDocument()
    expect(screen.getByText('117 vends')).toBeInTheDocument()
  })

  it('shows revenue share percentages', () => {
    render(<DeviceBreakdown devices={devices} />)
    expect(screen.getByText('61.8%')).toBeInTheDocument()
    expect(screen.getByText('38.2%')).toBeInTheDocument()
  })

  it('renders a title', () => {
    render(<DeviceBreakdown devices={devices} />)
    expect(screen.getByText('Devices')).toBeInTheDocument()
  })
})
