import { apiClient } from './client'
import type { AuthUser, LoginPayload, RegisterPayload } from '@/types/auth'

export const authApi = {
  async login(payload: LoginPayload): Promise<{ access_token: string; token_type: string }> {
    // OAuth2 Password Flow requiere form-urlencoded
    const form = new URLSearchParams()
    form.append('username', payload.email)
    form.append('password', payload.password)
    const { data } = await apiClient.post('/api/v1/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    return data
  },

  async register(payload: RegisterPayload): Promise<AuthUser> {
    const { data } = await apiClient.post<AuthUser>('/api/v1/auth/register', payload)
    return data
  },

  async me(): Promise<AuthUser> {
    const { data } = await apiClient.get<AuthUser>('/api/v1/users/me')
    return data
  },

  async forgotPassword(email: string): Promise<{ message: string }> {
    const { data } = await apiClient.post('/api/v1/auth/forgot-password', { email })
    return data
  },

  async resetPassword(token: string, new_password: string): Promise<{ message: string }> {
    const { data } = await apiClient.post('/api/v1/auth/reset-password', { token, new_password })
    return data
  },
}