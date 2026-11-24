import { RequireAuth } from './auth/RequireAuth'
import LoginPage from './routes/login'
import RegisterPage from './routes/register'
import CallbackPage from './routes/callback'
import SettingsPage from './routes/settings'

export default function App() {
  const path = window.location.pathname
  if (path === '/callback') return <CallbackPage />
  if (path === '/register') return <RegisterPage />
  if (path === '/login') return <LoginPage />
  // All other paths (including /) are protected
  return (
    <RequireAuth>
      <SettingsPage />
    </RequireAuth>
  )
}
