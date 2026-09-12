import { describe, it, expect } from 'vitest'
import { render, screen } from '../test-utils'
import StatCard from '@/components/StatCard'
import { DollarSign } from 'lucide-react'

describe('StatCard', () => {
  it('renders label and value', () => {
    render(<StatCard label="Total Revenue" value="$847.50" change={12.5} icon={DollarSign} />)
    expect(screen.getByText('Total Revenue')).toBeInTheDocument()
    expect(screen.getByText('$847.50')).toBeInTheDocument()
  })

  it('shows positive change with green styling', () => {
    render(<StatCard label="Revenue" value="$100" change={12.5} icon={DollarSign} />)
    const badge = screen.getByText('+12.5%')
    expect(badge.closest('[data-slot="badge"]')).toHaveClass('text-positive')
  })

  it('shows negative change with red styling', () => {
    render(<StatCard label="Revenue" value="$100" change={-3.2} icon={DollarSign} />)
    const badge = screen.getByText('-3.2%')
    expect(badge.closest('[data-slot="badge"]')).toHaveClass('text-negative')
  })

  it('shows zero change with neutral styling', () => {
    render(<StatCard label="Devices" value="2" change={0} icon={DollarSign} />)
    const badge = screen.getByText('0%')
    expect(badge.closest('[data-slot="badge"]')).toHaveClass('text-gray-400')
  })

  it('renders inside a card', () => {
    render(<StatCard label="Test" value="1" change={0} icon={DollarSign} />)
    expect(document.querySelector('[data-slot="card"]')).toBeInTheDocument()
  })
})
