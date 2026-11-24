import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import { UserManager, type User } from 'oidc-client-ts'
import { oidcConfig } from './OidcConfig'

export const userManager = new UserManager(oidcConfig)

interface AuthContextValue {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: () => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // getUser() reads from sessionStorage — no network call, no redirect
    userManager.getUser().then((u) => {
      // Treat expired users as logged out
      setUser(u && !u.expired ? u : null)
      setIsLoading(false)
    }).catch(() => {
      setUser(null)
      setIsLoading(false)
    })
    const cb = (u: User) => setUser(u)
    userManager.events.addUserLoaded(cb)
    userManager.events.addUserUnloaded(() => setUser(null))
    return () => {
      userManager.events.removeUserLoaded(cb)
    }
  }, [])

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user && !user.expired,
        login: () => userManager.signinRedirect(),
        logout: () => userManager.signoutRedirect(),
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
