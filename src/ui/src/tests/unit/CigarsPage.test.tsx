import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { http, HttpResponse } from 'msw'
import { server } from '../mocks/server'
import { mockAdminUser } from '../mocks/handlers'
import CigarsPage from '../../routes/cigars'

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

describe('CigarsPage', () => {
  it('renders the cigar list', async () => {
    render(wrap(<CigarsPage />))
    expect(await screen.findByText('Opus X')).toBeInTheDocument()
    // 'full' appears in table and in strength option, use getAllByText
    expect(screen.getAllByText('full').length).toBeGreaterThan(0)
  })

  it('renders brand_id association in the list', async () => {
    render(wrap(<CigarsPage />))
    await screen.findByText('Opus X')
    // Brand name shown from lookup (also appears in select option, use getAllByText)
    expect(screen.getAllByText('Arturo Fuente').length).toBeGreaterThan(0)
  })

  it('does not show admin controls for a member', async () => {
    render(wrap(<CigarsPage />))
    await screen.findByText('Opus X')
    expect(screen.queryByRole('button', { name: /new cigar/i })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /edit/i })).not.toBeInTheDocument()
  })

  it('shows admin controls for an admin user', async () => {
    server.use(http.get('*/v1/me', () => HttpResponse.json(mockAdminUser)))

    render(wrap(<CigarsPage />))
    expect(await screen.findByRole('button', { name: /new cigar/i })).toBeInTheDocument()
    expect(await screen.findByRole('button', { name: /edit/i })).toBeInTheDocument()
  })

  it('opens create modal when New cigar is clicked', async () => {
    server.use(http.get('*/v1/me', () => HttpResponse.json(mockAdminUser)))
    const user = userEvent.setup()

    render(wrap(<CigarsPage />))
    await user.click(await screen.findByRole('button', { name: /new cigar/i }))

    expect(await screen.findByRole('heading', { name: /new cigar/i })).toBeInTheDocument()
    expect(screen.getAllByRole('textbox')[0]).toBeInTheDocument()
  })

  it('shows validation error when name is empty on submit', async () => {
    server.use(http.get('*/v1/me', () => HttpResponse.json(mockAdminUser)))
    const user = userEvent.setup()

    render(wrap(<CigarsPage />))
    await user.click(await screen.findByRole('button', { name: /new cigar/i }))
    await user.click(await screen.findByRole('button', { name: /create cigar/i }))

    // Both name and brand_id are required — at least one "Required" appears
    expect((await screen.findAllByText('Required')).length).toBeGreaterThan(0)
  })

  it('submits create form and closes modal', async () => {
    server.use(http.get('*/v1/me', () => HttpResponse.json(mockAdminUser)))
    const user = userEvent.setup()

    render(wrap(<CigarsPage />))
    await user.click(await screen.findByRole('button', { name: /new cigar/i }))

    // Type the name (first textbox)
    const nameInput = screen.getAllByRole('textbox')[0]
    await user.type(nameInput, 'Padron 1964')

    // Select a brand from the brand combobox
    const selects = screen.getAllByRole('combobox')
    // First combobox is brand_id
    await user.selectOptions(selects[0], 'brand-uuid-001')

    await user.click(screen.getByRole('button', { name: /create cigar/i }))

    await waitFor(() => {
      expect(screen.queryByRole('heading', { name: /new cigar/i })).not.toBeInTheDocument()
    })
  })

  it('opens delete confirmation modal', async () => {
    server.use(http.get('*/v1/me', () => HttpResponse.json(mockAdminUser)))
    const user = userEvent.setup()

    render(wrap(<CigarsPage />))
    const deleteBtn = await screen.findByRole('button', { name: /^delete$/i })
    await user.click(deleteBtn)

    expect(await screen.findByRole('heading', { name: /delete cigar/i })).toBeInTheDocument()
    expect(screen.getAllByText(/Opus X/).length).toBeGreaterThan(0)
  })
})
