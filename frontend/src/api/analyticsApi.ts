import { apiClient } from './client'

export interface HeatmapLine {
  line: number
  error_count: number
  top_error: string
  users_affected: number
}

export interface ConceptStat {
  concept: string
  error_count: number
  users_affected: number
  pct_users: number
}

export interface ErrorTypeStat {
  type: string
  count: number
}

export interface ErrorHeatmapResponse {
  by_line: HeatmapLine[]
  by_concept: ConceptStat[]
  by_error_type: ErrorTypeStat[]
  period_days: number
  total_errors: number
}

export interface ConceptsRankingResponse {
  total_users: number
  concepts: ConceptStat[]
}

export interface RecentErrorEvent {
  id: string
  student: string
  challenge: string | null
  challenge_id: string | null
  error_type: string
  error_msg: string
  error_line: number | null
  created_at: string
}

export interface ChallengeErrorsResponse {
  challenge_id: string
  total_errors: number
  by_line: HeatmapLine[]
  recent: RecentErrorEvent[]
}

export const analyticsApi = {
  async getErrorHeatmap(params?: {
    course_id?: string
    challenge_id?: string
    days?: number
  }): Promise<ErrorHeatmapResponse> {
    const { data } = await apiClient.get<ErrorHeatmapResponse>(
      '/api/v1/admin/analytics/error-heatmap',
      { params },
    )
    return data
  },

  async getConceptsRanking(params?: {
    course_id?: string
    days?: number
  }): Promise<ConceptsRankingResponse> {
    const { data } = await apiClient.get<ConceptsRankingResponse>(
      '/api/v1/admin/analytics/concepts',
      { params },
    )
    return data
  },

  async getChallengeErrors(challengeId: string): Promise<ChallengeErrorsResponse> {
    const { data } = await apiClient.get<ChallengeErrorsResponse>(
      `/api/v1/admin/analytics/challenges/${challengeId}/errors`,
    )
    return data
  },
}
