import LoginPage from './routes/login'
import RegisterPage from './routes/register'
import CallbackPage from './routes/callback'
import SettingsPage from './routes/settings'
import LoungesPage from './routes/lounges'

export default function App() {
  const path = window.location.pathname
  if (path === '/callback') return <CallbackPage />
  if (path === '/register') return <RegisterPage />
  if (path === '/login') return <LoginPage />
  if (path === '/lounges') return <LoungesPage />
  if (path === '/settings') return <SettingsPage />
  // Default: redirect to lounges
  window.location.replace('/lounges')
  return null
}
