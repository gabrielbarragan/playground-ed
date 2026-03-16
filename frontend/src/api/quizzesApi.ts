import { apiClient } from './client'
import type { Quiz, QuizProgress, QuizAttempt, QuizStudentResult } from '@/types/quizzes'

export const quizzesApi = {
  // ── Admin ──────────────────────────────────────────────────
  async adminList(includeInactive = false): Promise<{ total: number; quizzes: Quiz[] }> {
    const { data } = await apiClient.get('/api/v1/admin/quizzes', {
      params: { include_inactive: includeInactive },
    })
    return data
  },

  async adminGet(id: string): Promise<Quiz> {
    const { data } = await apiClient.get(`/api/v1/admin/quizzes/${id}`)
    return data
  },

  async adminCreate(payload: object): Promise<Quiz> {
    const { data } = await apiClient.post('/api/v1/admin/quizzes', payload)
    return data
  },

  async adminUpdate(id: string, payload: object): Promise<Quiz> {
    const { data } = await apiClient.put(`/api/v1/admin/quizzes/${id}`, payload)
    return data
  },

  async adminToggle(id: string): Promise<Quiz> {
    const { data } = await apiClient.patch(`/api/v1/admin/quizzes/${id}/toggle`)
    return data
  },

  async addQuestion(quizId: string, payload: object): Promise<Quiz> {
    const { data } = await apiClient.post(`/api/v1/admin/quizzes/${quizId}/questions`, payload)
    return data
  },

  async updateQuestion(quizId: string, index: number, payload: object): Promise<Quiz> {
    const { data } = await apiClient.put(`/api/v1/admin/quizzes/${quizId}/questions/${index}`, payload)
    return data
  },

  async removeQuestion(quizId: string, index: number): Promise<Quiz> {
    const { data } = await apiClient.delete(`/api/v1/admin/quizzes/${quizId}/questions/${index}`)
    return data
  },

  async getResults(quizId: string): Promise<{ total: number; results: QuizStudentResult[] }> {
    const { data } = await apiClient.get(`/api/v1/admin/quizzes/${quizId}/results`)
    return data
  },

  async resetAttempt(quizId: string, userId: string): Promise<{ message: string }> {
    const { data } = await apiClient.delete(`/api/v1/admin/quizzes/${quizId}/attempts/${userId}`)
    return data
  },

  // ── Student ────────────────────────────────────────────────
  async list(): Promise<{ total: number; quizzes: QuizProgress[] }> {
    const { data } = await apiClient.get('/api/v1/quizzes')
    return data
  },

  async get(id: string): Promise<Quiz> {
    const { data } = await apiClient.get(`/api/v1/quizzes/${id}`)
    return data
  },

  async myResult(id: string): Promise<QuizAttempt> {
    const { data } = await apiClient.get(`/api/v1/quizzes/${id}/my-result`)
    return data
  },

  async submit(id: string, answers: number[]): Promise<QuizAttempt> {
    const { data } = await apiClient.post(`/api/v1/quizzes/${id}/submit`, { answers })
    return data
  },
}