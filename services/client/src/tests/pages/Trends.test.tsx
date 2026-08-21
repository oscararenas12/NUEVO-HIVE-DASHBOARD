import { render, screen } from '../test-utils'
import Trends from '@/pages/Trends'

describe('Trends', () => {
  it('renders the page title', () => {
    render(<Trends />)
    expect(screen.getByRole('heading', { name: /trends/i })).toBeInTheDocument()
  })
})
