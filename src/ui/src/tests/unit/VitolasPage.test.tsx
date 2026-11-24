import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { http, HttpResponse } from 'msw'
import { server } from '../mocks/server'
import { mockAdminUser } from '../mocks/handlers'
import VitolasPage from '../../routes/vitolas'

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

describe('VitolasPage', () => {
  it('renders the vitola list', async () => {
    render(wrap(<VitolasPage />))
    expect(await screen.findByText('Robusto')).toBeInTheDocument()
    expect(screen.getByText('5.00')).toBeInTheDocument()
  })

  it('does not show admin controls for a member', async () => {
    render(wrap(<VitolasPage />))
    await screen.findByText('Robusto')
    expect(screen.queryByRole('button', { name: /new vitola/i })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /edit/i })).not.toBeInTheDocument()
  })

  it('shows admin controls for an admin user', async () => {
    server.use(http.get('*/v1/me', () => HttpResponse.json(mockAdminUser)))

    render(wrap(<VitolasPage />))
    expect(await screen.findByRole('button', { name: /new vitola/i })).toBeInTheDocument()
    expect(await screen.findByRole('button', { name: /edit/i })).toBeInTheDocument()
  })

  it('opens create modal when New vitola is clicked', async () => {
    server.use(http.get('*/v1/me', () => HttpResponse.json(mockAdminUser)))
    const user = userEvent.setup()

    render(wrap(<VitolasPage />))
    await user.click(await screen.findByRole('button', { name: /new vitola/i }))

    expect(await screen.findByRole('heading', { name: /new vitola/i })).toBeInTheDocument()
    expect(screen.getAllByRole('textbox')[0]).toBeInTheDocument()
  })

  it('renders length_inches and ring_gauge inputs in the form', async () => {
    server.use(http.get('*/v1/me', () => HttpResponse.json(mockAdminUser)))
    const user = userEvent.setup()

    render(wrap(<VitolasPage />))
    await user.click(await screen.findByRole('button', { name: /new vitola/i }))

    expect(screen.getByPlaceholderText('e.g. 5.00')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('e.g. 50')).toBeInTheDocument()
  })

  it('shows validation error when name is empty on submit', async () => {
    server.use(http.get('*/v1/me', () => HttpResponse.json(mockAdminUser)))
    const user = userEvent.setup()

    render(wrap(<VitolasPage />))
    await user.click(await screen.findByRole('button', { name: /new vitola/i }))
    await user.click(await screen.findByRole('button', { name: /create vitola/i }))

    expect(await screen.findByText('Required')).toBeInTheDocument()
  })

  it('submits create form and closes modal', async () => {
    server.use(http.get('*/v1/me', () => HttpResponse.json(mockAdminUser)))
    const user = userEvent.setup()

    render(wrap(<VitolasPage />))
    await user.click(await screen.findByRole('button', { name: /new vitola/i }))

    const nameInput = screen.getAllByRole('textbox')[0]
    await user.type(nameInput, 'Toro')
    await user.click(screen.getByRole('button', { name: /create vitola/i }))

    await waitFor(() => {
      expect(screen.queryByRole('heading', { name: /new vitola/i })).not.toBeInTheDocument()
    })
  })

  it('opens delete confirmation modal', async () => {
    server.use(http.get('*/v1/me', () => HttpResponse.json(mockAdminUser)))
    const user = userEvent.setup()

    render(wrap(<VitolasPage />))
    const deleteBtn = await screen.findByRole('button', { name: /^delete$/i })
    await user.click(deleteBtn)

    expect(await screen.findByRole('heading', { name: /delete vitola/i })).toBeInTheDocument()
    expect(screen.getAllByText(/Robusto/).length).toBeGreaterThan(0)
  })
})
