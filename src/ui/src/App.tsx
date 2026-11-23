import LoginPage from './routes/login'
import CallbackPage from './routes/callback'
import SettingsPage from './routes/settings'

export default function App() {
  const path = window.location.pathname
  if (path === '/callback') return <CallbackPage />
  if (path === '/login') return <LoginPage />
  return <SettingsPage />
}
