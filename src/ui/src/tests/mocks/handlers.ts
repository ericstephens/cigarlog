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

export const handlers = [
  http.get('*/v1/me', () => HttpResponse.json(mockUser)),
  http.patch('*/v1/me', async ({ request }) => {
    const body = (await request.json()) as Record<string, unknown>
    return HttpResponse.json({ ...mockUser, ...body })
  }),
]
