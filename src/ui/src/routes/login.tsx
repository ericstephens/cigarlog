import { useAuth } from '../auth/AuthProvider'
import { Button } from '../components/ui/Button'

export default function LoginPage() {
  const { login } = useAuth()
  return (
    <div className="flex h-screen items-center justify-center bg-zinc-950">
      <div className="flex flex-col items-center gap-6">
        <h1 className="text-2xl font-bold text-white">Cigar Log</h1>
        <p className="text-sm text-zinc-400">Track your smokes.</p>
        <Button onClick={() => void login()}>Sign in</Button>
      </div>
    </div>
  )
}
