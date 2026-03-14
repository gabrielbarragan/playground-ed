import { apiClient } from './client'

export type UserRole = 'student' | 'admin' | 'superadmin'

export interface SuperAdminUser {
  id: string
  first_name: string
  last_name: string
  email: string
  is_active: boolean
  is_admin: boolean
  is_superadmin: boolean
  role: UserRole
  total_points: number
  course: { id: string; name: string; code: string } | null
  created_at: string
  last_login: string | null
}

export interface SuperAdminCourse {
  id: string
  name: string
  code: string
  description: string
  is_active: boolean
  created_at: string
}

export interface CreateCoursePayload {
  name: string
  code: string
  description?: string
}

export const superAdminApi = {
  async listUsers(params?: { include_inactive?: boolean }): Promise<{ total: number; users: SuperAdminUser[] }> {
    const { data } = await apiClient.get('/api/v1/superadmin/users', { params })
    return data
  },

  async updateRole(userId: string, role: UserRole): Promise<SuperAdminUser> {
    const { data } = await apiClient.put(`/api/v1/superadmin/users/${userId}/role`, { role })
    return data
  },

  async listCourses(): Promise<{ total: number; courses: SuperAdminCourse[] }> {
    const { data } = await apiClient.get('/api/v1/superadmin/courses')
    return data
  },

  async createCourse(payload: CreateCoursePayload): Promise<SuperAdminCourse> {
    const { data } = await apiClient.post('/api/v1/superadmin/courses', payload)
    return data
  },

  async toggleCourse(courseId: string): Promise<SuperAdminCourse> {
    const { data } = await apiClient.patch(`/api/v1/superadmin/courses/${courseId}/toggle`)
    return data
  },
}