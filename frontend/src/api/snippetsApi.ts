import { apiClient } from './client'
import type { Snippet, SaveSnippetPayload, UpdateSnippetPayload } from '@/types/snippets'

export const snippetsApi = {
  async list(): Promise<Snippet[]> {
    const { data } = await apiClient.get<Snippet[]>('/api/v1/snippets/')
    return data
  },

  async save(payload: SaveSnippetPayload): Promise<Snippet> {
    const { data } = await apiClient.post<Snippet>('/api/v1/snippets/', {
      ...payload,
      language: payload.language ?? 'python',
      tags: payload.tags ?? [],
    })
    return data
  },

  async update(id: string, payload: UpdateSnippetPayload): Promise<Snippet> {
    const { data } = await apiClient.put<Snippet>(`/api/v1/snippets/${id}`, {
      ...payload,
      tags: payload.tags ?? [],
    })
    return data
  },

  async remove(id: string): Promise<void> {
    await apiClient.delete(`/api/v1/snippets/${id}`)
  },
}