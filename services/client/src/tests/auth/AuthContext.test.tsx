import { describe, expect, it, vi, beforeEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { AuthProvider, useAuth } from '@/auth/AuthContext'
import * as authApi from '@/api/auth'

vi.mock('@/api/auth', () => ({
  login: vi.fn(),
  register: vi.fn(),
  getStatus: vi.fn(),
  refresh: vi.fn(),
  logout: vi.fn(),
}))

const mockUser = {
  id: 1,
  username: 'alice',
  email: 'alice@example.com',
  role: 'employee',
  is_active: true,
  created_at: '2026-01-01T00:00:00Z',
}

beforeEach(() => {
  vi.mocked(authApi.refresh).mockRejectedValue(new Error('no cookie'))
})

function renderAuth() {
  return renderHook(() => useAuth(), { wrapper: AuthProvider })
}

describe('AuthProvider', () => {
  it('starts unauthenticated after failed refresh', async () => {
    const { result } = renderAuth()
    await waitFor(() => expect(result.current.isLoading).toBe(false))
    expect(result.current.isAuthenticated).toBe(false)
    expect(result.current.user).toBeNull()
  })

  it('restores session on mount when refresh succeeds', async () => {
    vi.mocked(authApi.refresh).mockResolvedValueOnce({ access_token: 'tok', token_type: 'bearer' })
    vi.mocked(authApi.getStatus).mockResolvedValueOnce(mockUser)

    const { result } = renderAuth()
    await waitFor(() => expect(result.current.isLoading).toBe(false))
    expect(result.current.isAuthenticated).toBe(true)
    expect(result.current.user).toEqual(mockUser)
  })

  it('login sets user and token', async () => {
    vi.mocked(authApi.login).mockResolvedValueOnce({ access_token: 'tok', token_type: 'bearer' })
    vi.mocked(authApi.getStatus).mockResolvedValueOnce(mockUser)

    const { result } = renderAuth()
    await waitFor(() => expect(result.current.isLoading).toBe(false))

    await act(() => result.current.login('alice@example.com', 'pass'))
    expect(result.current.isAuthenticated).toBe(true)
    expect(result.current.user).toEqual(mockUser)
    expect(result.current.token).toBe('tok')
  })

  it('login propagates API errors', async () => {
    vi.mocked(authApi.login).mockRejectedValueOnce(new Error('Invalid credentials'))

    const { result } = renderAuth()
    await waitFor(() => expect(result.current.isLoading).toBe(false))

    await expect(act(() => result.current.login('a@b.com', 'wrong'))).rejects.toThrow(
      'Invalid credentials'
    )
    expect(result.current.isAuthenticated).toBe(false)
  })

  it('logout clears user and token', async () => {
    vi.mocked(authApi.login).mockResolvedValueOnce({ access_token: 'tok', token_type: 'bearer' })
    vi.mocked(authApi.getStatus).mockResolvedValueOnce(mockUser)
    vi.mocked(authApi.logout).mockResolvedValueOnce(undefined)

    const { result } = renderAuth()
    await waitFor(() => expect(result.current.isLoading).toBe(false))

    await act(() => result.current.login('alice@example.com', 'pass'))
    expect(result.current.isAuthenticated).toBe(true)

    await act(() => result.current.logout())
    expect(result.current.isAuthenticated).toBe(false)
    expect(result.current.user).toBeNull()
    expect(result.current.token).toBeNull()
  })
})
