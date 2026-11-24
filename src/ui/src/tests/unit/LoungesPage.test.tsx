import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { http, HttpResponse } from 'msw'
import { server } from '../mocks/server'
import { mockAdminUser } from '../mocks/handlers'
import LoungesPage from '../../routes/lounges'

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

describe('LoungesPage', () => {
  it('renders the lounge list', async () => {
    render(wrap(<LoungesPage />))
    expect(await screen.findByText('The Humidor')).toBeInTheDocument()
    expect(screen.getByText('Chicago, IL, USA')).toBeInTheDocument()
  })

  it('renders address and postal code in table', async () => {
    render(wrap(<LoungesPage />))
    await screen.findByText('The Humidor')
    expect(screen.getByText('123 Smoke Blvd 60601')).toBeInTheDocument()
  })

  it('does not show admin controls for a member', async () => {
    render(wrap(<LoungesPage />))
    await screen.findByText('The Humidor')
    expect(screen.queryByRole('button', { name: /new lounge/i })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /edit/i })).not.toBeInTheDocument()
  })

  it('shows admin controls for an admin user', async () => {
    // Override /v1/me to return admin role
    server.use(http.get('*/v1/me', () => HttpResponse.json(mockAdminUser)))

    render(wrap(<LoungesPage />))
    expect(await screen.findByRole('button', { name: /new lounge/i })).toBeInTheDocument()
    expect(await screen.findByRole('button', { name: /edit/i })).toBeInTheDocument()
  })

  it('opens create modal when New lounge is clicked', async () => {
    server.use(http.get('*/v1/me', () => HttpResponse.json(mockAdminUser)))
    const user = userEvent.setup()

    render(wrap(<LoungesPage />))
    await user.click(await screen.findByRole('button', { name: /new lounge/i }))

    // The modal title "New lounge" appears in the dialog header
    expect(await screen.findByRole('heading', { name: /new lounge/i })).toBeInTheDocument()
    // The form renders with an autoFocus name input (first textbox in the form)
    expect(screen.getAllByRole('textbox')[0]).toBeInTheDocument()
  })

  it('renders state picklist in the form', async () => {
    server.use(http.get('*/v1/me', () => HttpResponse.json(mockAdminUser)))
    const user = userEvent.setup()

    render(wrap(<LoungesPage />))
    await user.click(await screen.findByRole('button', { name: /new lounge/i }))

    // StateSelect renders as a combobox / listbox role in some renderers; check by option text
    const stateSelect = screen.getByRole('combobox')
    expect(stateSelect).toBeInTheDocument()
    // Illinois should be an option
    expect(screen.getByRole('option', { name: /IL – Illinois/i })).toBeInTheDocument()
  })

  it('shows validation error when name is empty on submit', async () => {
    server.use(http.get('*/v1/me', () => HttpResponse.json(mockAdminUser)))
    const user = userEvent.setup()

    render(wrap(<LoungesPage />))
    await user.click(await screen.findByRole('button', { name: /new lounge/i }))
    await user.click(await screen.findByRole('button', { name: /create lounge/i }))

    expect(await screen.findByText('Required')).toBeInTheDocument()
  })

  it('submits create form and closes modal', async () => {
    server.use(http.get('*/v1/me', () => HttpResponse.json(mockAdminUser)))
    const user = userEvent.setup()

    render(wrap(<LoungesPage />))
    await user.click(await screen.findByRole('button', { name: /new lounge/i }))

    // Type into the first text input (Name field)
    const nameInput = screen.getAllByRole('textbox')[0]
    await user.type(nameInput, 'Brand New Lounge')
    await user.click(screen.getByRole('button', { name: /create lounge/i }))

    await waitFor(() => {
      expect(screen.queryByRole('heading', { name: /new lounge/i })).not.toBeInTheDocument()
    })
  })

  it('opens delete confirmation modal', async () => {
    server.use(http.get('*/v1/me', () => HttpResponse.json(mockAdminUser)))
    const user = userEvent.setup()

    render(wrap(<LoungesPage />))
    const deleteBtn = await screen.findByRole('button', { name: /^delete$/i })
    await user.click(deleteBtn)

    expect(await screen.findByRole('heading', { name: /delete lounge/i })).toBeInTheDocument()
    // The lounge name appears in the confirmation text
    expect(screen.getAllByText(/The Humidor/).length).toBeGreaterThan(0)
  })
})
