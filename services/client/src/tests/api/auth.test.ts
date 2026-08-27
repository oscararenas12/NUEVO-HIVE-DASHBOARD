import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { login, register, getStatus, refresh, logout } from '@/api/auth'

const mockFetch = vi.fn()

beforeEach(() => {
  vi.stubGlobal('fetch', mockFetch)
})

afterEach(() => {
  vi.restoreAllMocks()
})

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

describe('login', () => {
  it('posts credentials and returns token', async () => {
    mockFetch.mockResolvedValueOnce(
      jsonResponse({ access_token: 'tok123', token_type: 'bearer' })
    )
    const result = await login('a@b.com', 'pass')
    expect(result).toEqual({ access_token: 'tok123', token_type: 'bearer' })
    expect(mockFetch).toHaveBeenCalledWith(
      '/auth/login',
      expect.objectContaining({
        method: 'POST',
        credentials: 'include',
        body: JSON.stringify({ email: 'a@b.com', password: 'pass' }),
      })
    )
  })

  it('throws on invalid credentials', async () => {
    mockFetch.mockResolvedValueOnce(
      jsonResponse({ detail: 'Invalid credentials' }, 401)
    )
    await expect(login('a@b.com', 'wrong')).rejects.toThrow('Invalid credentials')
  })
})

describe('register', () => {
  it('posts registration data and returns user', async () => {
    const user = { id: 1, username: 'alice', email: 'a@b.com', role: 'employee', is_active: true, created_at: '2026-01-01T00:00:00Z' }
    mockFetch.mockResolvedValueOnce(jsonResponse(user, 201))
    const result = await register('alice', 'a@b.com', 'pass')
    expect(result).toEqual(user)
    expect(mockFetch).toHaveBeenCalledWith(
      '/auth/register',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ username: 'alice', email: 'a@b.com', password: 'pass' }),
      })
    )
  })

  it('throws on duplicate email', async () => {
    mockFetch.mockResolvedValueOnce(
      jsonResponse({ detail: 'Username or email already registered' }, 400)
    )
    await expect(register('alice', 'dup@b.com', 'pass')).rejects.toThrow(
      'Username or email already registered'
    )
  })
})

describe('getStatus', () => {
  it('sends bearer token and returns user', async () => {
    const user = { id: 1, username: 'alice', email: 'a@b.com', role: 'employee', is_active: true, created_at: '2026-01-01T00:00:00Z' }
    mockFetch.mockResolvedValueOnce(jsonResponse(user))
    const result = await getStatus('tok123')
    expect(result).toEqual(user)
    expect(mockFetch).toHaveBeenCalledWith(
      '/auth/status',
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: 'Bearer tok123' }),
        credentials: 'include',
      })
    )
  })

  it('throws when not authenticated', async () => {
    mockFetch.mockResolvedValueOnce(jsonResponse({ detail: 'Not authenticated' }, 401))
    await expect(getStatus('bad')).rejects.toThrow('Not authenticated')
  })
})

describe('refresh', () => {
  it('posts to refresh and returns new token', async () => {
    mockFetch.mockResolvedValueOnce(
      jsonResponse({ access_token: 'new-tok', token_type: 'bearer' })
    )
    const result = await refresh()
    expect(result).toEqual({ access_token: 'new-tok', token_type: 'bearer' })
    expect(mockFetch).toHaveBeenCalledWith(
      '/auth/refresh',
      expect.objectContaining({ method: 'POST', credentials: 'include' })
    )
  })

  it('throws when no refresh cookie', async () => {
    mockFetch.mockResolvedValueOnce(jsonResponse({ detail: 'Missing refresh token' }, 401))
    await expect(refresh()).rejects.toThrow('Missing refresh token')
  })
})

describe('logout', () => {
  it('posts to logout', async () => {
    mockFetch.mockResolvedValueOnce(jsonResponse({ message: 'logged out' }))
    await logout()
    expect(mockFetch).toHaveBeenCalledWith(
      '/auth/logout',
      expect.objectContaining({ method: 'POST', credentials: 'include' })
    )
  })
})
