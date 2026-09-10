import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'

import { authService } from '../services/auth'
import { clearAccessToken, getAccessToken, setAccessToken } from '../services/tokenStorage'

export const AuthContext = createContext({
  user: null,
  token: null,
  isRestoring: false,
  login: async () => {},
  superadminLogin: async () => {},
  logout: () => {},
})

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => getAccessToken())
  const [user, setUser] = useState(null)
  const [isRestoring, setIsRestoring] = useState(Boolean(getAccessToken()))

  useEffect(() => {
    let active = true
    const storedToken = getAccessToken()
    if (!storedToken) {
      setIsRestoring(false)
      return () => { active = false }
    }

    authService.getCurrentUser()
      .then(({ user: currentUser }) => {
        if (active) setUser(currentUser)
      })
      .catch((error) => {
        if (active && error.status === 401) {
          clearAccessToken()
          setToken(null)
          setUser(null)
        }
      })
      .finally(() => active && setIsRestoring(false))

    return () => { active = false }
  }, [])

  const establishSession = useCallback(({ access_token: accessToken, user: authenticatedUser }) => {
    setAccessToken(accessToken)
    setToken(accessToken)
    setUser(authenticatedUser)
    return authenticatedUser
  }, [])

  const login = useCallback(async (email, password) => {
    return establishSession(await authService.login(email, password))
  }, [establishSession])

  const superadminLogin = useCallback(async (email, password) => {
    return establishSession(await authService.superadminLogin(email, password))
  }, [establishSession])

  const logout = useCallback(() => {
    clearAccessToken()
    setToken(null)
    setUser(null)
  }, [])

  const value = useMemo(
    () => ({ user, token, isRestoring, login, superadminLogin, logout }),
    [user, token, isRestoring, login, superadminLogin, logout],
  )

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
