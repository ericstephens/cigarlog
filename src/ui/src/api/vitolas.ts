import { fetchWithAuth } from './client'

export interface Vitola {
  id: string
  name: string
  length_inches: string | null
  ring_gauge: number | null
  created_at: string
  updated_at: string
}

export interface VitolaWrite {
  name: string
  length_inches?: string
  ring_gauge?: number
}

export const getVitolas = (token: string): Promise<Vitola[]> =>
  fetchWithAuth('/v1/vitolas', token) as Promise<Vitola[]>

export const createVitola = (token: string, data: VitolaWrite): Promise<Vitola> =>
  fetchWithAuth('/v1/vitolas', token, {
    method: 'POST',
    body: JSON.stringify(data),
  }) as Promise<Vitola>

export const updateVitola = (token: string, id: string, data: Partial<VitolaWrite>): Promise<Vitola> =>
  fetchWithAuth(`/v1/vitolas/${id}`, token, {
    method: 'PATCH',
    body: JSON.stringify(data),
  }) as Promise<Vitola>

export const deleteVitola = (token: string, id: string): Promise<void> =>
  fetchWithAuth(`/v1/vitolas/${id}`, token, { method: 'DELETE' }) as Promise<void>
