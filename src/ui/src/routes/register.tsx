import { useState } from 'react'
import { userManager } from '../auth/AuthProvider'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { FormField } from '../components/ui/FormField'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export default function RegisterPage() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      // Create the user in Keycloak via the backend proxy.
      const res = await fetch(`${API_BASE}/v1/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, display_name: name.trim() }),
      })
      if (!res.ok) {
        const body = (await res.json().catch(() => ({}))) as { detail?: string }
        throw new Error(body.detail ?? 'Registration failed.')
      }

      // User exists in Keycloak — sign in directly (no redirect).
      await userManager.signinResourceOwnerCredentials({ username: email, password })
      window.location.replace('/')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed.')
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-950 px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-white">Cigar Log</h1>
          <p className="mt-2 text-sm text-zinc-400">Create your account</p>
        </div>

        <form onSubmit={(e) => void handleSubmit(e)} className="flex flex-col gap-4">
          <FormField label="Display name">
            <Input
              type="text"
              placeholder="Your name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              autoFocus
            />
          </FormField>

          <FormField label="Email">
            <Input
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </FormField>

          <FormField label="Password">
            <Input
              type="password"
              placeholder="Choose a password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </FormField>

          {error && <p className="text-xs text-red-400">{error}</p>}

          <Button type="submit" disabled={loading} className="mt-2 w-full py-2.5">
            {loading ? 'Creating account…' : 'Create account'}
          </Button>
        </form>

        <p className="mt-6 text-center text-sm text-zinc-500">
          Already have an account?{' '}
          <a href="/login" className="text-amber-500 hover:underline">
            Sign in
          </a>
        </p>
      </div>
    </div>
  )
}
