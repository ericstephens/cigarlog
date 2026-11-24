import { fetchWithAuth } from './client'

export interface Cigar {
  id: string
  name: string
  brand_id: string
  factory_id: string | null
  vitola_id: string | null
  wrapper: string | null
  binder_origin: string | null
  filler_origin: string | null
  strength: string | null
  msrp: string | null
  description: string | null
  created_at: string
  updated_at: string
}

export interface CigarWrite {
  name: string
  brand_id: string
  factory_id?: string
  vitola_id?: string
  wrapper?: string
  binder_origin?: string
  filler_origin?: string
  strength?: string
  msrp?: string
  description?: string
}

export const getCigars = (token: string): Promise<Cigar[]> =>
  fetchWithAuth('/v1/cigars', token) as Promise<Cigar[]>

export const createCigar = (token: string, data: CigarWrite): Promise<Cigar> =>
  fetchWithAuth('/v1/cigars', token, {
    method: 'POST',
    body: JSON.stringify(data),
  }) as Promise<Cigar>

export const updateCigar = (token: string, id: string, data: Partial<CigarWrite>): Promise<Cigar> =>
  fetchWithAuth(`/v1/cigars/${id}`, token, {
    method: 'PATCH',
    body: JSON.stringify(data),
  }) as Promise<Cigar>

export const deleteCigar = (token: string, id: string): Promise<void> =>
  fetchWithAuth(`/v1/cigars/${id}`, token, { method: 'DELETE' }) as Promise<void>
