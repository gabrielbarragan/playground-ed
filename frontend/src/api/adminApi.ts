import { apiClient } from './client'

export interface AdminUser {
  id: string
  first_name: string
  last_name: string
  email: string
  is_active: boolean
  is_admin: boolean
  total_points: number
  course: { id: string; name: string; code: string } | null
  created_at: string
  last_login: string | null
}

export interface UsersListResponse {
  total: number
  users: AdminUser[]
}

export interface GlobalStats {
  users: {
    active: number
    inactive: number
    total: number
    active_last_7_days: number
  }
  executions: {
    last_7_days: number
  }
  courses: { id: string; name: string; code: string; active_users: number }[]
}

export const adminApi = {
  async getStats(): Promise<GlobalStats> {
    const { data } = await apiClient.get<GlobalStats>('/api/v1/admin/stats')
    return data
  },

  async listUsers(params?: { course_id?: string; include_inactive?: boolean }): Promise<UsersListResponse> {
    const { data } = await apiClient.get<UsersListResponse>('/api/v1/admin/users', { params })
    return data
  },

  async activateUser(id: string): Promise<AdminUser> {
    const { data } = await apiClient.put<AdminUser>(`/api/v1/admin/users/${id}/activate`)
    return data
  },

  async deactivateUser(id: string): Promise<AdminUser> {
    const { data } = await apiClient.put<AdminUser>(`/api/v1/admin/users/${id}/deactivate`)
    return data
  },
}