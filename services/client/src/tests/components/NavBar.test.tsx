import { render, screen } from '../test-utils'
import NavBar from '@/components/NavBar'

describe('NavBar', () => {
  it('renders Overview link', () => {
    render(<NavBar />)
    expect(screen.getByRole('link', { name: /overview/i })).toBeInTheDocument()
  })

  it('renders Slot Performance link', () => {
    render(<NavBar />)
    expect(screen.getByRole('link', { name: /slot performance/i })).toBeInTheDocument()
  })

  it('renders Trends link', () => {
    render(<NavBar />)
    expect(screen.getByRole('link', { name: /trends/i })).toBeInTheDocument()
  })

  it('highlights the active link', () => {
    render(<NavBar />, { routerProps: { initialEntries: ['/slots'] } })
    const activeLink = screen.getByRole('link', { name: /slot performance/i })
    expect(activeLink.className).toMatch(/bg-/)
  })
})
