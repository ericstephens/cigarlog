import { fetchWithAuth } from './client'

export interface Brand {
  id: string
  name: string
  country: string | null
  website: string | null
  notes: string | null
  created_at: string
  updated_at: string
}

export interface BrandWrite {
  name: string
  country?: string
  website?: string
  notes?: string
}

export const getBrands = (token: string): Promise<Brand[]> =>
  fetchWithAuth('/v1/brands', token) as Promise<Brand[]>

export const createBrand = (token: string, data: BrandWrite): Promise<Brand> =>
  fetchWithAuth('/v1/brands', token, {
    method: 'POST',
    body: JSON.stringify(data),
  }) as Promise<Brand>

export const updateBrand = (token: string, id: string, data: Partial<BrandWrite>): Promise<Brand> =>
  fetchWithAuth(`/v1/brands/${id}`, token, {
    method: 'PATCH',
    body: JSON.stringify(data),
  }) as Promise<Brand>

export const deleteBrand = (token: string, id: string): Promise<void> =>
  fetchWithAuth(`/v1/brands/${id}`, token, { method: 'DELETE' }) as Promise<void>
