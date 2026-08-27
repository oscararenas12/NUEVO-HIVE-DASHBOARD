import { render } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { vi } from 'vitest'
import App from '../App'

vi.mock('@/api/auth', () => ({
  refresh: vi.fn().mockRejectedValue(new Error('no cookie')),
  login: vi.fn(),
  register: vi.fn(),
  getStatus: vi.fn(),
  logout: vi.fn(),
}))

describe('App', () => {
  it('renders without crashing', () => {
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>
    )
  })
})
