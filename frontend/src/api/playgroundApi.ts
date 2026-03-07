import { apiClient } from './client'
import type { CodeExecutionRequest, ExecutionResult } from '@/types/playground'

export const playgroundApi = {
  /**
   * POST /api/code-runs
   * Envía código Python al sandbox y retorna stdout/stderr/return_code.
   */
  async runCode(payload: CodeExecutionRequest): Promise<ExecutionResult> {
    const { data } = await apiClient.post<ExecutionResult>('/api/code-runs', payload)
    return data
  },
}