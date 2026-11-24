import { fetchWithAuth } from './client'

export interface Factory {
  id: string
  name: string
  city: string | null
  country: string | null
  notes: string | null
  created_at: string
  updated_at: string
}

export interface FactoryWrite {
  name: string
  city?: string
  country?: string
  notes?: string
}

export const getFactories = (token: string): Promise<Factory[]> =>
  fetchWithAuth('/v1/factories', token) as Promise<Factory[]>

export const createFactory = (token: string, data: FactoryWrite): Promise<Factory> =>
  fetchWithAuth('/v1/factories', token, {
    method: 'POST',
    body: JSON.stringify(data),
  }) as Promise<Factory>

export const updateFactory = (token: string, id: string, data: Partial<FactoryWrite>): Promise<Factory> =>
  fetchWithAuth(`/v1/factories/${id}`, token, {
    method: 'PATCH',
    body: JSON.stringify(data),
  }) as Promise<Factory>

export const deleteFactory = (token: string, id: string): Promise<void> =>
  fetchWithAuth(`/v1/factories/${id}`, token, { method: 'DELETE' }) as Promise<void>
