import { fetchWithAuth } from './client'

export interface UserProfile {
  id: string
  email: string
  display_name: string
  role: string
  unit_system: 'imperial' | 'metric'
  timezone: string
  trusted: boolean
  created_at: string
  updated_at: string
}

export interface UserUpdate {
  display_name?: string
  unit_system?: 'imperial' | 'metric'
  timezone?: string
}

export const getMe = (token: string): Promise<UserProfile> =>
  fetchWithAuth('/v1/me', token) as Promise<UserProfile>

export const patchMe = (token: string, data: UserUpdate): Promise<UserProfile> =>
  fetchWithAuth('/v1/me', token, {
    method: 'PATCH',
    body: JSON.stringify(data),
  }) as Promise<UserProfile>
