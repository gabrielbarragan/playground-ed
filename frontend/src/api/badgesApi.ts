import { apiClient } from './client'

export interface Badge {
  emoji: string
  label: string
  order: number
}

export const badgesApi = {
  async list(): Promise<Badge[]> {
    const { data } = await apiClient.get<Badge[]>('/api/v1/badges')
    return data
  },

  async setMyBadge(emoji: string): Promise<void> {
    await apiClient.put('/api/v1/users/me/badge', { emoji })
  },
}