import { useEffect, useState } from 'react'
import { userManager } from './AuthProvider'

export function Callback() {
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    userManager
      .signinRedirectCallback()
      .then(() => {
        window.location.replace('/settings')
      })
      .catch((e: unknown) => {
        setError(e instanceof Error ? e.message : String(e))
      })
  }, [])

  if (error) {
    return (
      <div className="flex h-screen items-center justify-center bg-zinc-950">
        <div className="max-w-sm text-center">
          <p className="mb-2 text-sm font-medium text-red-400">Sign-in failed</p>
          <p className="text-xs text-zinc-500">{error}</p>
          <a href="/login" className="mt-4 inline-block text-sm text-amber-500 underline">
            Try again
          </a>
        </div>
      </div>
    )
  }

  return (
    <div className="flex h-screen items-center justify-center bg-zinc-950 text-zinc-400">
      Signing in…
    </div>
  )
}
