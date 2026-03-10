import { apiClient } from './client'

export interface ActivityDay {
  date: string
  executions: number
  successful_executions: number
  lines_of_code: number
}

export interface HeatmapResponse {
  days: ActivityDay[]
  total_executions: number
  streak_days: number
}

export interface RankingEntry {
  rank: number
  id: string
  first_name: string
  last_name: string
  total_points: number
}

export interface RankingResponse {
  course: { id: string; name: string; code: string }
  ranking: RankingEntry[]
}

export const dashboardApi = {
  async myActivity(): Promise<HeatmapResponse> {
    const { data } = await apiClient.get<HeatmapResponse>('/api/v1/dashboard/activity')
    return data
  },

  async courseRanking(courseId: string, limit = 20): Promise<RankingResponse> {
    const { data } = await apiClient.get<RankingResponse>(
      `/api/v1/dashboard/courses/${courseId}/ranking`,
      { params: { limit } },
    )
    return data
  },
}