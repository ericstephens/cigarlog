import { http, HttpResponse } from 'msw'

const mockUser = {
  id: 'test-uuid-001',
  email: 'test@example.com',
  display_name: 'Test User',
  role: 'member',
  unit_system: 'imperial',
  timezone: 'UTC',
  trusted: false,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
}

export const mockAdminUser = { ...mockUser, role: 'admin' }

const mockLounges = [
  {
    id: 'lounge-uuid-001',
    name: 'The Humidor',
    city: 'Chicago',
    state: 'IL',
    country: 'USA',
    address: '123 Smoke Blvd',
    postal_code: '60601',
    website: null,
    notes: null,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  },
]

export const handlers = [
  http.get('*/v1/me', () => HttpResponse.json(mockUser)),
  http.patch('*/v1/me', async ({ request }) => {
    const body = (await request.json()) as Record<string, unknown>
    return HttpResponse.json({ ...mockUser, ...body })
  }),

  http.get('*/v1/lounges', () => HttpResponse.json(mockLounges)),
  http.post('*/v1/lounges', async ({ request }) => {
    const body = (await request.json()) as Record<string, unknown>
    return HttpResponse.json(
      { id: 'lounge-uuid-new', ...body, created_at: '2026-01-01T00:00:00Z', updated_at: '2026-01-01T00:00:00Z' },
      { status: 201 },
    )
  }),
  http.patch('*/v1/lounges/:id', async ({ request, params }) => {
    const body = (await request.json()) as Record<string, unknown>
    return HttpResponse.json({ ...mockLounges[0], ...body, id: params.id })
  }),
  http.delete('*/v1/lounges/:id', () => new HttpResponse(null, { status: 204 })),
]
