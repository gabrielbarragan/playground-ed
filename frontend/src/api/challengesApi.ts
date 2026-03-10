import { apiClient } from './client'
import type { Challenge, ChallengeProgress, Attempt } from '@/types/challenges'

export const challengesApi = {
  // ── Admin ──────────────────────────────────────────────────
  async adminList(includeInactive = false): Promise<{ total: number; challenges: Challenge[] }> {
    const { data } = await apiClient.get('/api/v1/admin/challenges', {
      params: { include_inactive: includeInactive },
    })
    return data
  },

  async adminGet(id: string): Promise<Challenge> {
    const { data } = await apiClient.get(`/api/v1/admin/challenges/${id}`)
    return data
  },

  async adminCreate(payload: object): Promise<Challenge> {
    const { data } = await apiClient.post('/api/v1/admin/challenges', payload)
    return data
  },

  async adminUpdate(id: string, payload: object): Promise<Challenge> {
    const { data } = await apiClient.put(`/api/v1/admin/challenges/${id}`, payload)
    return data
  },

  async adminDelete(id: string): Promise<void> {
    await apiClient.delete(`/api/v1/admin/challenges/${id}`)
  },

  async addTestCase(challengeId: string, payload: object): Promise<Challenge> {
    const { data } = await apiClient.post(
      `/api/v1/admin/challenges/${challengeId}/test-cases`,
      payload,
    )
    return data
  },

  async removeTestCase(challengeId: string, index: number): Promise<Challenge> {
    const { data } = await apiClient.delete(
      `/api/v1/admin/challenges/${challengeId}/test-cases/${index}`,
    )
    return data
  },

  // ── Admin – Submissions ────────────────────────────────────
  async pendingSubmissions(challengeId?: string): Promise<{ total: number; submissions: Attempt[] }> {
    const { data } = await apiClient.get('/api/v1/admin/submissions/pending', {
      params: challengeId ? { challenge_id: challengeId } : undefined,
    })
    return data
  },

  async approveSubmission(attemptId: string, feedback = ''): Promise<Attempt> {
    const { data } = await apiClient.put(`/api/v1/admin/submissions/${attemptId}/approve`, { feedback })
    return data
  },

  async rejectSubmission(attemptId: string, feedback = ''): Promise<Attempt> {
    const { data } = await apiClient.put(`/api/v1/admin/submissions/${attemptId}/reject`, { feedback })
    return data
  },

  // ── Student ────────────────────────────────────────────────
  async list(): Promise<{ total: number; challenges: Challenge[] }> {
    const { data } = await apiClient.get('/api/v1/challenges')
    return data
  },

  async get(id: string): Promise<Challenge> {
    const { data } = await apiClient.get(`/api/v1/challenges/${id}`)
    return data
  },

  async myProgress(): Promise<{
    total_challenges: number
    solved: number
    pending_review: number
    challenges: ChallengeProgress[]
  }> {
    const { data } = await apiClient.get('/api/v1/challenges/my-progress')
    return data
  },

  async myAttempts(id: string): Promise<{ total: number; already_passed: boolean; attempts: Attempt[] }> {
    const { data } = await apiClient.get(`/api/v1/challenges/${id}/my-attempts`)
    return data
  },

  async submit(id: string, code: string): Promise<Attempt> {
    const { data } = await apiClient.post(`/api/v1/challenges/${id}/submit`, { code })
    return data
  },
}