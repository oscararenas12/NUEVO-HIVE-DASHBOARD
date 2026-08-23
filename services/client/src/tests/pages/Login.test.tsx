import { render, screen } from '../test-utils'
import Login from '@/pages/Login'

describe('Login', () => {
  it('renders the page title', () => {
    render(<Login />)
    expect(screen.getByRole('heading', { name: /login/i })).toBeInTheDocument()
  })
})
