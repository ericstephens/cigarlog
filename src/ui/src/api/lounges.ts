import { fetchWithAuth } from './client'

export interface Lounge {
  id: string
  name: string
  city: string | null
  state: string | null
  country: string | null
  website: string | null
  notes: string | null
  created_at: string
  updated_at: string
}

export interface LoungeWrite {
  name: string
  city?: string
  state?: string
  country?: string
  website?: string
  notes?: string
}

export const getLounges = (token: string): Promise<Lounge[]> =>
  fetchWithAuth('/v1/lounges', token) as Promise<Lounge[]>

export const createLounge = (token: string, data: LoungeWrite): Promise<Lounge> =>
  fetchWithAuth('/v1/lounges', token, {
    method: 'POST',
    body: JSON.stringify(data),
  }) as Promise<Lounge>

export const updateLounge = (token: string, id: string, data: Partial<LoungeWrite>): Promise<Lounge> =>
  fetchWithAuth(`/v1/lounges/${id}`, token, {
    method: 'PATCH',
    body: JSON.stringify(data),
  }) as Promise<Lounge>

export const deleteLounge = (token: string, id: string): Promise<void> =>
  fetchWithAuth(`/v1/lounges/${id}`, token, { method: 'DELETE' }) as Promise<void>
