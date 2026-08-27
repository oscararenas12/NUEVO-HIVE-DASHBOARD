import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import type { UserRead } from '@/api/auth'
import * as authApi from '@/api/auth'

interface AuthState {
  user: UserRead | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (username: string, email: string, password: string) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthState | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserRead | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    authApi
      .refresh()
      .then(({ access_token }) => {
        setToken(access_token)
        return authApi.getStatus(access_token)
      })
      .then(setUser)
      .catch(() => {})
      .finally(() => setIsLoading(false))
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    const { access_token } = await authApi.login(email, password)
    setToken(access_token)
    const u = await authApi.getStatus(access_token)
    setUser(u)
  }, [])

  const register = useCallback(
    async (username: string, email: string, password: string) => {
      await authApi.register(username, email, password)
    },
    [],
  )

  const logoutFn = useCallback(async () => {
    await authApi.logout()
    setToken(null)
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        logout: logoutFn,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
