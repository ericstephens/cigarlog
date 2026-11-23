import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import SettingsPage from '../../routes/settings'

vi.mock('../../auth/AuthProvider', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../../auth/AuthProvider')>()
  return {
    ...actual,
    useAuth: vi.fn(() => ({
      user: { access_token: 'test-token', expired: false },
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
    })),
  }
})

vi.mock('../../auth/RequireAuth', () => ({
  RequireAuth: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}))

function wrap(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return <QueryClientProvider client={qc}>{ui}</QueryClientProvider>
}

describe('SettingsForm', () => {
  it('renders with values loaded from API', async () => {
    render(wrap(<SettingsPage />))
    expect(await screen.findByDisplayValue('Test User')).toBeInTheDocument()
  })

  it('shows validation error when display_name is empty', async () => {
    const user = userEvent.setup()
    render(wrap(<SettingsPage />))
    const input = await screen.findByDisplayValue('Test User')
    await user.clear(input)
    await user.click(screen.getByRole('button', { name: /save/i }))
    expect(await screen.findByText('Required')).toBeInTheDocument()
  })

  it('submits PATCH when form is valid', async () => {
    const user = userEvent.setup()
    render(wrap(<SettingsPage />))
    const input = await screen.findByDisplayValue('Test User')
    await user.clear(input)
    await user.type(input, 'New Name')
    await user.click(screen.getByRole('button', { name: /save/i }))
    expect(await screen.findByText('Saved.')).toBeInTheDocument()
  })
})
