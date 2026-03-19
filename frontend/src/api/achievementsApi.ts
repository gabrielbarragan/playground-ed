import { apiClient } from './client'

export interface SandboxAchievement {
  id: string
  name: string
  description: string
  icon: string
  trigger_type: string
  trigger_value: string
  points_bonus: number
  is_active: boolean
  created_at: string
}

export interface UserAchievement {
  id: string
  earned_at: string
  achievement: {
    id: string
    name: string
    description: string
    icon: string
    points_bonus: number
  }
}

export interface MyAchievementsResponse {
  earned: UserAchievement[]
  locked: { id: string; icon: string; name: string; description: string; points_bonus: number }[]
  total: number
  earned_count: number
}

export const achievementsApi = {
  // ── Student ─────────────────────────────────────────────
  async myAchievements(): Promise<MyAchievementsResponse> {
    const { data } = await apiClient.get('/api/v1/users/me/sandbox-achievements')
    return data
  },

  // ── Admin ────────────────────────────────────────────────
  async adminList(includeInactive = false): Promise<SandboxAchievement[]> {
    const { data } = await apiClient.get('/api/v1/admin/sandbox-achievements', {
      params: { include_inactive: includeInactive },
    })
    return data
  },

  async adminCreate(payload: object): Promise<SandboxAchievement> {
    const { data } = await apiClient.post('/api/v1/admin/sandbox-achievements', payload)
    return data
  },

  async adminUpdate(id: string, payload: object): Promise<SandboxAchievement> {
    const { data } = await apiClient.patch(`/api/v1/admin/sandbox-achievements/${id}`, payload)
    return data
  },

  async adminDelete(id: string): Promise<void> {
    await apiClient.delete(`/api/v1/admin/sandbox-achievements/${id}`)
  },

  async adminSeed(): Promise<{ created: number }> {
    const { data } = await apiClient.post('/api/v1/admin/sandbox-achievements/seed')
    return data
  },
}