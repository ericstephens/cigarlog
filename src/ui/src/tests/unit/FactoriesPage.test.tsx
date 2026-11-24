import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { http, HttpResponse } from 'msw'
import { server } from '../mocks/server'
import { mockAdminUser } from '../mocks/handlers'
import FactoriesPage from '../../routes/factories'

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

describe('FactoriesPage', () => {
  it('renders the factory list', async () => {
    render(wrap(<FactoriesPage />))
    expect(await screen.findByText('General Cigar Company')).toBeInTheDocument()
    expect(screen.getByText('Santiago')).toBeInTheDocument()
  })

  it('does not show admin controls for a member', async () => {
    render(wrap(<FactoriesPage />))
    await screen.findByText('General Cigar Company')
    expect(screen.queryByRole('button', { name: /new factory/i })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /edit/i })).not.toBeInTheDocument()
  })

  it('shows admin controls for an admin user', async () => {
    server.use(http.get('*/v1/me', () => HttpResponse.json(mockAdminUser)))

    render(wrap(<FactoriesPage />))
    expect(await screen.findByRole('button', { name: /new factory/i })).toBeInTheDocument()
    expect(await screen.findByRole('button', { name: /edit/i })).toBeInTheDocument()
  })

  it('opens create modal when New factory is clicked', async () => {
    server.use(http.get('*/v1/me', () => HttpResponse.json(mockAdminUser)))
    const user = userEvent.setup()

    render(wrap(<FactoriesPage />))
    await user.click(await screen.findByRole('button', { name: /new factory/i }))

    expect(await screen.findByRole('heading', { name: /new factory/i })).toBeInTheDocument()
    expect(screen.getAllByRole('textbox')[0]).toBeInTheDocument()
  })

  it('shows validation error when name is empty on submit', async () => {
    server.use(http.get('*/v1/me', () => HttpResponse.json(mockAdminUser)))
    const user = userEvent.setup()

    render(wrap(<FactoriesPage />))
    await user.click(await screen.findByRole('button', { name: /new factory/i }))
    await user.click(await screen.findByRole('button', { name: /create factory/i }))

    expect(await screen.findByText('Required')).toBeInTheDocument()
  })

  it('submits create form and closes modal', async () => {
    server.use(http.get('*/v1/me', () => HttpResponse.json(mockAdminUser)))
    const user = userEvent.setup()

    render(wrap(<FactoriesPage />))
    await user.click(await screen.findByRole('button', { name: /new factory/i }))

    const nameInput = screen.getAllByRole('textbox')[0]
    await user.type(nameInput, 'TABSA')
    await user.click(screen.getByRole('button', { name: /create factory/i }))

    await waitFor(() => {
      expect(screen.queryByRole('heading', { name: /new factory/i })).not.toBeInTheDocument()
    })
  })

  it('opens delete confirmation modal', async () => {
    server.use(http.get('*/v1/me', () => HttpResponse.json(mockAdminUser)))
    const user = userEvent.setup()

    render(wrap(<FactoriesPage />))
    const deleteBtn = await screen.findByRole('button', { name: /^delete$/i })
    await user.click(deleteBtn)

    expect(await screen.findByRole('heading', { name: /delete factory/i })).toBeInTheDocument()
    expect(screen.getAllByText(/General Cigar Company/).length).toBeGreaterThan(0)
  })
})
