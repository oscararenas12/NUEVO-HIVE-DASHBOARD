import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '../test-utils'

vi.mock('recharts', () => import('../__mocks__/recharts'))

import PaymentTypes from '@/components/PaymentTypes'
import type { PaymentBreakdown } from '@/api/dashboard'

const data: PaymentBreakdown[] = [
  { payment_type: 'Credit (EMV Contactless)', revenue: 412.50, vends: 152, percentage: 48.7 },
  { payment_type: 'Cash', revenue: 148.00, vends: 58, percentage: 17.5 },
  { payment_type: 'Credit (Apple Pay EMV)', revenue: 126.00, vends: 46, percentage: 14.9 },
]

describe('PaymentTypes', () => {
  it('renders the title', () => {
    render(<PaymentTypes data={data} />)
    expect(screen.getByText('Payment Methods')).toBeInTheDocument()
  })

  it('renders payment type names in the legend', () => {
    render(<PaymentTypes data={data} />)
    expect(screen.getByText('Credit (EMV Contactless)')).toBeInTheDocument()
    expect(screen.getByText('Cash')).toBeInTheDocument()
    expect(screen.getByText('Credit (Apple Pay EMV)')).toBeInTheDocument()
  })

  it('renders percentage values', () => {
    render(<PaymentTypes data={data} />)
    expect(screen.getByText('48.7%')).toBeInTheDocument()
    expect(screen.getByText('17.5%')).toBeInTheDocument()
  })

  it('renders inside a card', () => {
    render(<PaymentTypes data={data} />)
    expect(document.querySelector('[data-slot="card"]')).toBeInTheDocument()
  })
})
