import { apiClient } from './client'

export const usersApi = {
  async changeMyEmail(new_email: string): Promise<{ message: string }> {
    const { data } = await apiClient.put('/api/v1/users/me/email', { new_email })
    return data
  },

  async confirmEmail(token: string): Promise<{ message: string }> {
    const { data } = await apiClient.get('/api/v1/users/confirm-email', { params: { token } })
    return data
  },
}
