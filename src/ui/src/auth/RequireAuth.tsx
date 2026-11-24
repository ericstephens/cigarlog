import { useEffect, type ReactNode } from 'react'
import { useAuth } from './AuthProvider'

export function RequireAuth({ children }: { children: ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth()

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      window.location.replace('/login')
    }
  }, [isLoading, isAuthenticated])

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-zinc-950 text-zinc-400">
        Loading…
      </div>
    )
  }
  if (!isAuthenticated) return null
  return <>{children}</>
}
