import { createContext, useContext } from 'react'

const AuthContext = createContext({ user: null, token: null })

export function AuthProvider({ children }) {
  return (
    <AuthContext.Provider value={{ user: null, token: null }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
