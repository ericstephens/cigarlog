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

export const mockBrands = [
  {
    id: 'brand-uuid-001',
    name: 'Arturo Fuente',
    country: 'Dominican Republic',
    website: null,
    notes: null,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  },
]

export const mockFactories = [
  {
    id: 'factory-uuid-001',
    name: 'General Cigar Company',
    city: 'Santiago',
    country: 'Dominican Republic',
    notes: null,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  },
]

export const mockVitolas = [
  {
    id: 'vitola-uuid-001',
    name: 'Robusto',
    length_inches: '5.00',
    ring_gauge: 50,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  },
]

export const mockCigars = [
  {
    id: 'cigar-uuid-001',
    name: 'Opus X',
    brand_id: 'brand-uuid-001',
    factory_id: null,
    vitola_id: null,
    wrapper: null,
    binder_origin: null,
    filler_origin: null,
    strength: 'full',
    msrp: '30.00',
    description: null,
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

  http.get('*/v1/brands', () => HttpResponse.json(mockBrands)),
  http.post('*/v1/brands', async ({ request }) => {
    const body = (await request.json()) as Record<string, unknown>
    return HttpResponse.json(
      { id: 'brand-uuid-new', ...body, created_at: '2026-01-01T00:00:00Z', updated_at: '2026-01-01T00:00:00Z' },
      { status: 201 },
    )
  }),
  http.patch('*/v1/brands/:id', async ({ request, params }) => {
    const body = (await request.json()) as Record<string, unknown>
    return HttpResponse.json({ ...mockBrands[0], ...body, id: params.id })
  }),
  http.delete('*/v1/brands/:id', () => new HttpResponse(null, { status: 204 })),

  http.get('*/v1/factories', () => HttpResponse.json(mockFactories)),
  http.post('*/v1/factories', async ({ request }) => {
    const body = (await request.json()) as Record<string, unknown>
    return HttpResponse.json(
      { id: 'factory-uuid-new', ...body, created_at: '2026-01-01T00:00:00Z', updated_at: '2026-01-01T00:00:00Z' },
      { status: 201 },
    )
  }),
  http.patch('*/v1/factories/:id', async ({ request, params }) => {
    const body = (await request.json()) as Record<string, unknown>
    return HttpResponse.json({ ...mockFactories[0], ...body, id: params.id })
  }),
  http.delete('*/v1/factories/:id', () => new HttpResponse(null, { status: 204 })),

  http.get('*/v1/vitolas', () => HttpResponse.json(mockVitolas)),
  http.post('*/v1/vitolas', async ({ request }) => {
    const body = (await request.json()) as Record<string, unknown>
    return HttpResponse.json(
      { id: 'vitola-uuid-new', ...body, created_at: '2026-01-01T00:00:00Z', updated_at: '2026-01-01T00:00:00Z' },
      { status: 201 },
    )
  }),
  http.patch('*/v1/vitolas/:id', async ({ request, params }) => {
    const body = (await request.json()) as Record<string, unknown>
    return HttpResponse.json({ ...mockVitolas[0], ...body, id: params.id })
  }),
  http.delete('*/v1/vitolas/:id', () => new HttpResponse(null, { status: 204 })),

  http.get('*/v1/cigars', () => HttpResponse.json(mockCigars)),
  http.post('*/v1/cigars', async ({ request }) => {
    const body = (await request.json()) as Record<string, unknown>
    return HttpResponse.json(
      { id: 'cigar-uuid-new', ...body, created_at: '2026-01-01T00:00:00Z', updated_at: '2026-01-01T00:00:00Z' },
      { status: 201 },
    )
  }),
  http.patch('*/v1/cigars/:id', async ({ request, params }) => {
    const body = (await request.json()) as Record<string, unknown>
    return HttpResponse.json({ ...mockCigars[0], ...body, id: params.id })
  }),
  http.delete('*/v1/cigars/:id', () => new HttpResponse(null, { status: 204 })),
]
