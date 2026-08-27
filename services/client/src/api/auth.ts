const API_BASE = import.meta.env.VITE_API_URL ?? ''

export interface UserRead {
  id: number
  username: string
  email: string
  role: string
  is_active: boolean
  created_at: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

async function handleResponse<T>(res: Response, fallback: string): Promise<T> {
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: fallback }))
    throw new Error(err.detail ?? fallback)
  }
  return res.json()
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ email, password }),
  })
  return handleResponse(res, 'Login failed')
}

export async function register(
  username: string,
  email: string,
  password: string,
): Promise<UserRead> {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, email, password }),
  })
  return handleResponse(res, 'Registration failed')
}

export async function getStatus(token: string): Promise<UserRead> {
  const res = await fetch(`${API_BASE}/auth/status`, {
    headers: { Authorization: `Bearer ${token}` },
    credentials: 'include',
  })
  return handleResponse(res, 'Not authenticated')
}

export async function refresh(): Promise<TokenResponse> {
  const res = await fetch(`${API_BASE}/auth/refresh`, {
    method: 'POST',
    credentials: 'include',
  })
  return handleResponse(res, 'Refresh failed')
}

export async function logout(): Promise<void> {
  await fetch(`${API_BASE}/auth/logout`, {
    method: 'POST',
    credentials: 'include',
  })
}
