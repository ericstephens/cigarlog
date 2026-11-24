import { useState } from 'react'
import { userManager } from '../auth/AuthProvider'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { FormField } from '../components/ui/FormField'

export default function RegisterPage() {
  const [email, setEmail] = useState('')
  const [name, setName] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      // Pass email and display name as hints to the OIDC provider.
      // The mock server uses login_hint to pre-fill the subject field.
      // The app creates the app_user row automatically on first login.
      await userManager.signinRedirect({
        login_hint: email,
        extraQueryParams: { name },
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
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
            <Input type="password" placeholder="Choose a password" defaultValue="" />
          </FormField>

          {error && <p className="text-xs text-red-400">{error}</p>}

          <Button type="submit" disabled={loading} className="mt-2 w-full py-2.5">
            {loading ? 'Redirecting…' : 'Create account'}
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
