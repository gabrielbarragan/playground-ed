import axios from 'axios'
import type { AxiosInstance, AxiosError } from 'axios'
import type { ApiError } from '@/types/playground'

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL ?? ''
const TIMEOUT_MS = 9_000 // 1s menos que el TIMEOUT del backend (10s)

export const apiClient: AxiosInstance = axios.create({
  baseURL: BACKEND_URL,
  timeout: TIMEOUT_MS,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    const apiError: ApiError = {
      message: 'Error desconocido',
      isTimeout: false,
      isNetworkError: false,
    }

    if (error.code === 'ECONNABORTED') {
      apiError.message = 'La ejecución superó el tiempo máximo permitido (9s).'
      apiError.isTimeout = true
      return Promise.reject(apiError)
    }

    if (!error.response) {
      apiError.message = 'No se pudo conectar con el servidor. Verificá que el backend esté corriendo.'
      apiError.isNetworkError = true
      return Promise.reject(apiError)
    }

    apiError.statusCode = error.response.status
    apiError.message = `Error del servidor: ${error.response.status}`

    if (error.response.status === 401) {
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }

    return Promise.reject(apiError)
  },
)