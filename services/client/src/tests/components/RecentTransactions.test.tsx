import { describe, it, expect } from 'vitest'
import { render, screen } from '../test-utils'
import RecentTransactions from '@/components/RecentTransactions'
import type { Transaction } from '@/api/dashboard'

const transactions: Transaction[] = [
  { item_ref: '22248127354', device: 'VK200044724', item_date: '2026-09-11T16:19:45', amount: 2.50, slot_code: '0B06', payment_type: 'Credit (EMV Contactless)', settle_status: 'SETTLED' },
  { item_ref: '22248127356', device: 'VK200044729', item_date: '2026-09-11T14:55:33', amount: 2.00, slot_code: '0A02', payment_type: 'Cash', settle_status: 'SETTLED' },
]

describe('RecentTransactions', () => {
  it('renders the title', () => {
    render(<RecentTransactions transactions={transactions} />)
    expect(screen.getByText('Recent Transactions')).toBeInTheDocument()
  })

  it('renders column headers', () => {
    render(<RecentTransactions transactions={transactions} />)
    expect(screen.getByText('Date')).toBeInTheDocument()
    expect(screen.getByText('Device')).toBeInTheDocument()
    expect(screen.getByText('Slot')).toBeInTheDocument()
    expect(screen.getByText('Amount')).toBeInTheDocument()
    expect(screen.getByText('Payment')).toBeInTheDocument()
  })

  it('renders transaction data', () => {
    render(<RecentTransactions transactions={transactions} />)
    expect(screen.getByText('0B06')).toBeInTheDocument()
    expect(screen.getByText('0A02')).toBeInTheDocument()
    expect(screen.getByText('$2.50')).toBeInTheDocument()
    expect(screen.getByText('$2.00')).toBeInTheDocument()
  })

  it('renders payment types', () => {
    render(<RecentTransactions transactions={transactions} />)
    expect(screen.getByText('Credit (EMV Contactless)')).toBeInTheDocument()
    expect(screen.getByText('Cash')).toBeInTheDocument()
  })

  it('renders inside a card', () => {
    render(<RecentTransactions transactions={transactions} />)
    expect(document.querySelector('[data-slot="card"]')).toBeInTheDocument()
  })
})
