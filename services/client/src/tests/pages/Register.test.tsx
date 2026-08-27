import { describe, expect, it, vi, beforeEach } from 'vitest'
import { render, screen, userEvent } from '../test-utils'
import Register from '@/pages/Register'

const mockRegister = vi.fn()
const mockNavigate = vi.fn()

vi.mock('@/auth/AuthContext', () => ({
  useAuth: () => ({
    register: mockRegister,
    isAuthenticated: false,
    isLoading: false,
  }),
}))

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom')
  return { ...actual, useNavigate: () => mockNavigate }
})

beforeEach(() => {
  vi.clearAllMocks()
})

describe('Register', () => {
  it('renders username, email, and password fields', () => {
    render(<Register />)
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
  })

  it('renders a submit button', () => {
    render(<Register />)
    expect(screen.getByRole('button', { name: /create account/i })).toBeInTheDocument()
  })

  it('renders a link to login', () => {
    render(<Register />)
    expect(screen.getByRole('link', { name: /sign in/i })).toBeInTheDocument()
  })

  it('calls register and navigates to login on success', async () => {
    mockRegister.mockResolvedValueOnce(undefined)
    render(<Register />)

    const user = userEvent.setup()
    await user.type(screen.getByLabelText(/username/i), 'alice')
    await user.type(screen.getByLabelText(/email/i), 'alice@example.com')
    await user.type(screen.getByLabelText(/password/i), 's3cret')
    await user.click(screen.getByRole('button', { name: /create account/i }))

    expect(mockRegister).toHaveBeenCalledWith('alice', 'alice@example.com', 's3cret')
    expect(mockNavigate).toHaveBeenCalledWith('/login')
  })

  it('shows error message on failed registration', async () => {
    mockRegister.mockRejectedValueOnce(new Error('Username or email already registered'))
    render(<Register />)

    const user = userEvent.setup()
    await user.type(screen.getByLabelText(/username/i), 'alice')
    await user.type(screen.getByLabelText(/email/i), 'dup@example.com')
    await user.type(screen.getByLabelText(/password/i), 's3cret')
    await user.click(screen.getByRole('button', { name: /create account/i }))

    expect(
      await screen.findByText('Username or email already registered')
    ).toBeInTheDocument()
  })
})
