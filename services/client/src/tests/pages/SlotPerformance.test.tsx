import { render, screen } from '../test-utils'
import SlotPerformance from '@/pages/SlotPerformance'

describe('SlotPerformance', () => {
  it('renders the page title', () => {
    render(<SlotPerformance />)
    expect(screen.getByRole('heading', { name: /slot performance/i })).toBeInTheDocument()
  })
})
