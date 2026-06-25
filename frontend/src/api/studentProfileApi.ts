import { apiClient } from './client'

export const studentProfileApi = {
  async getSummary(userId: string) {
    const { data } = await apiClient.get(`/api/v1/admin/users/${userId}/profile-summary`)
    return data
  },

  async getChallenges(userId: string) {
    const { data } = await apiClient.get(`/api/v1/admin/users/${userId}/challenges`)
    return data
  },

  async getQuizzes(userId: string) {
    const { data } = await apiClient.get(`/api/v1/admin/users/${userId}/quizzes`)
    return data
  },

  async getAttempts(userId: string, limit = 10) {
    const { data } = await apiClient.get(`/api/v1/admin/users/${userId}/attempts`, {
      params: { limit },
    })
    return data
  },

  async getSnippets(userId: string, limit = 20) {
    const { data } = await apiClient.get(`/api/v1/admin/users/${userId}/snippets`, {
      params: { limit },
    })
    return data
  },

  async getSnippetDetail(userId: string, snippetId: string) {
    const { data } = await apiClient.get(`/api/v1/admin/users/${userId}/snippets/${snippetId}`)
    return data as { id: string; title: string; code: string; language: string; tags: string[]; created_at: string; updated_at: string }
  },

  async getAchievements(userId: string) {
    const { data } = await apiClient.get(`/api/v1/admin/users/${userId}/achievements`)
    return data
  },

  async getPointsBreakdown(userId: string) {
    const { data } = await apiClient.get(`/api/v1/admin/users/${userId}/points-breakdown`)
    return data
  },
}
