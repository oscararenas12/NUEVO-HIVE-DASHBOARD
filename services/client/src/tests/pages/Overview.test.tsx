import { render, screen } from '../test-utils'
import Overview from '@/pages/Overview'

describe('Overview', () => {
  it('renders the page title', () => {
    render(<Overview />)
    expect(screen.getByRole('heading', { name: /overview/i })).toBeInTheDocument()
  })
})
