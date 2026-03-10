import { apiClient } from './client'
import type { Course } from '@/types/auth'

export const coursesApi = {
  async list(): Promise<Course[]> {
    const { data } = await apiClient.get<Course[]>('/api/v1/courses/')
    return data
  },
}