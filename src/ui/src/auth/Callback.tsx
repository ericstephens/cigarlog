import { useEffect } from 'react'
import { userManager } from './AuthProvider'

export function Callback() {
  useEffect(() => {
    userManager
      .signinRedirectCallback()
      .then(() => {
        window.location.replace('/settings')
      })
      .catch(console.error)
  }, [])

  return (
    <div className="flex h-screen items-center justify-center bg-zinc-950 text-zinc-400">
      Signing in…
    </div>
  )
}
