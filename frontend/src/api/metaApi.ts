import { apiClient } from './client'
import type { HealthResponse, VersionResponse, MetaResponse } from '@/types/playground'

export const metaApi = {
  /** GET /health */
  async health(): Promise<HealthResponse> {
    const { data } = await apiClient.get<HealthResponse>('/health')
    return data
  },

  /** GET /version */
  async version(): Promise<VersionResponse> {
    const { data } = await apiClient.get<VersionResponse>('/version')
    return data
  },

  /** GET / */
  async meta(): Promise<MetaResponse> {
    const { data } = await apiClient.get<MetaResponse>('/')
    return data
  },
}