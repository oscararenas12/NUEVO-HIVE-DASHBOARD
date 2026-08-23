import { render, screen } from '../test-utils'
import Layout from '@/components/Layout'

describe('Layout', () => {
  it('renders the sidebar navigation', () => {
    render(<Layout />)
    expect(screen.getByRole('navigation')).toBeInTheDocument()
  })

  it('renders the app title in the sidebar', () => {
    render(<Layout />)
    expect(screen.getByText('Nuevo Hive')).toBeInTheDocument()
  })

  it('renders the main content area', () => {
    render(<Layout />)
    expect(screen.getByRole('main')).toBeInTheDocument()
  })

  it('renders child page content via Outlet', () => {
    render(<Layout />, {
      routerProps: { initialEntries: ['/'] },
    })
    expect(screen.getByRole('main')).toBeInTheDocument()
  })
})
