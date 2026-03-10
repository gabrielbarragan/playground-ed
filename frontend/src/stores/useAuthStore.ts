import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/authApi'
import { badgesApi } from '@/api/badgesApi'
import type { AuthUser, LoginPayload, RegisterPayload } from '@/types/auth'

const TOKEN_KEY = 'auth_token'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<AuthUser | null>(null)
  const token = ref<string | null>(localStorage.getItem(TOKEN_KEY))

  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.is_admin ?? false)

  function _saveToken(t: string) {
    token.value = t
    localStorage.setItem(TOKEN_KEY, t)
  }

  function _clearSession() {
    token.value = null
    user.value = null
    localStorage.removeItem(TOKEN_KEY)
  }

  async function login(payload: LoginPayload): Promise<void> {
    const res = await authApi.login(payload)
    _saveToken(res.access_token)
    user.value = await authApi.me()
  }

  async function register(payload: RegisterPayload): Promise<void> {
    await authApi.register(payload)
    await login({ email: payload.email, password: payload.password })
  }

  async function fetchMe(): Promise<boolean> {
    if (!token.value) return false
    try {
      user.value = await authApi.me()
      return true
    } catch {
      _clearSession()
      return false
    }
  }

  async function setBadge(emoji: string): Promise<void> {
    await badgesApi.setMyBadge(emoji)
    if (user.value) {
      user.value = { ...user.value, badge: emoji }
    }
  }

  function logout() {
    _clearSession()
  }

  return {
    user,
    token,
    isAuthenticated,
    isAdmin,
    login,
    register,
    fetchMe,
    setBadge,
    logout,
  }
})