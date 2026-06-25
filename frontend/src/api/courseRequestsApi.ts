import { apiClient } from './client'

export interface CourseChangeRequest {
  id: string
  user: {
    id: string
    first_name: string
    last_name: string
    email: string
  }
  from_course: { id: string; name: string; code: string }
  to_course: { id: string; name: string; code: string }
  reason: string
  status: 'pending' | 'approved' | 'rejected'
  rejection_reason: string
  resolved_by: string | null
  resolved_at: string | null
  created_at: string
}

export const courseRequestsApi = {
  async createRequest(to_course_id: string, reason: string = ''): Promise<CourseChangeRequest> {
    const { data } = await apiClient.post('/api/v1/users/me/course-change-request', { to_course_id, reason })
    return data
  },

  async getMyPendingRequest(): Promise<CourseChangeRequest | null> {
    const { data } = await apiClient.get('/api/v1/users/me/course-change-request')
    return data
  },

  async listPendingRequests(): Promise<{ total: number; requests: CourseChangeRequest[] }> {
    const { data } = await apiClient.get('/api/v1/admin/course-change-requests')
    return data
  },

  async resolveRequest(requestId: string, action: 'approve' | 'reject', rejection_reason: string = ''): Promise<CourseChangeRequest> {
    const { data } = await apiClient.put(`/api/v1/admin/course-change-requests/${requestId}/resolve`, { action, rejection_reason })
    return data
  },
}
