import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { http, HttpResponse } from 'msw'
import { server } from '../mocks/server'
import { mockAdminUser } from '../mocks/handlers'
import BrandsPage from '../../routes/brands'

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

describe('BrandsPage', () => {
  it('renders the brand list', async () => {
    render(wrap(<BrandsPage />))
    expect(await screen.findByText('Arturo Fuente')).toBeInTheDocument()
    expect(screen.getByText('Dominican Republic')).toBeInTheDocument()
  })

  it('does not show admin controls for a member', async () => {
    render(wrap(<BrandsPage />))
    await screen.findByText('Arturo Fuente')
    expect(screen.queryByRole('button', { name: /new brand/i })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /edit/i })).not.toBeInTheDocument()
  })

  it('shows admin controls for an admin user', async () => {
    server.use(http.get('*/v1/me', () => HttpResponse.json(mockAdminUser)))

    render(wrap(<BrandsPage />))
    expect(await screen.findByRole('button', { name: /new brand/i })).toBeInTheDocument()
    expect(await screen.findByRole('button', { name: /edit/i })).toBeInTheDocument()
  })

  it('opens create modal when New brand is clicked', async () => {
    server.use(http.get('*/v1/me', () => HttpResponse.json(mockAdminUser)))
    const user = userEvent.setup()

    render(wrap(<BrandsPage />))
    await user.click(await screen.findByRole('button', { name: /new brand/i }))

    expect(await screen.findByRole('heading', { name: /new brand/i })).toBeInTheDocument()
    expect(screen.getAllByRole('textbox')[0]).toBeInTheDocument()
  })

  it('shows validation error when name is empty on submit', async () => {
    server.use(http.get('*/v1/me', () => HttpResponse.json(mockAdminUser)))
    const user = userEvent.setup()

    render(wrap(<BrandsPage />))
    await user.click(await screen.findByRole('button', { name: /new brand/i }))
    await user.click(await screen.findByRole('button', { name: /create brand/i }))

    expect(await screen.findByText('Required')).toBeInTheDocument()
  })

  it('submits create form and closes modal', async () => {
    server.use(http.get('*/v1/me', () => HttpResponse.json(mockAdminUser)))
    const user = userEvent.setup()

    render(wrap(<BrandsPage />))
    await user.click(await screen.findByRole('button', { name: /new brand/i }))

    const nameInput = screen.getAllByRole('textbox')[0]
    await user.type(nameInput, 'Padron')
    await user.click(screen.getByRole('button', { name: /create brand/i }))

    await waitFor(() => {
      expect(screen.queryByRole('heading', { name: /new brand/i })).not.toBeInTheDocument()
    })
  })

  it('opens delete confirmation modal', async () => {
    server.use(http.get('*/v1/me', () => HttpResponse.json(mockAdminUser)))
    const user = userEvent.setup()

    render(wrap(<BrandsPage />))
    const deleteBtn = await screen.findByRole('button', { name: /^delete$/i })
    await user.click(deleteBtn)

    expect(await screen.findByRole('heading', { name: /delete brand/i })).toBeInTheDocument()
    expect(screen.getAllByText(/Arturo Fuente/).length).toBeGreaterThan(0)
  })
})
