import { useState } from 'react'
import { userManager } from '../auth/AuthProvider'
import { Button } from '../components/ui/Button'

export default function LoginPage() {
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function handleLogin() {
    setError(null)
    setLoading(true)
    try {
      await userManager.signinRedirect()
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
      setLoading(false)
    }
  }

  return (
    <div className="flex h-screen items-center justify-center bg-zinc-950">
      <div className="flex flex-col items-center gap-6">
        <h1 className="text-2xl font-bold text-white">Cigar Log</h1>
        <p className="text-sm text-zinc-400">Track your smokes.</p>
        <Button onClick={() => void handleLogin()} disabled={loading}>
          {loading ? 'Redirecting…' : 'Sign in'}
        </Button>
        {error && (
          <p className="max-w-sm text-center text-xs text-red-400">
            {error}
          </p>
        )}
      </div>
    </div>
  )
}
