<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-logo">
        <svg width="26" height="26" viewBox="0 0 24 24" fill="none">
          <path
            d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14H9V8h2v8zm4 0h-2V8h2v8z"
            fill="#cba6f7"
          />
        </svg>
        <span class="auth-logo-text">FANAMA Playground</span>
      </div>

      <div v-if="loading" class="status-box">
        <span class="spinner" />
        <p>Confirmando tu nuevo correo...</p>
      </div>

      <div v-else-if="success" class="success-box">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" style="margin-bottom:0.75rem">
          <circle cx="12" cy="12" r="10" stroke="#a6e3a1" stroke-width="2"/>
          <path d="M8 12l3 3 5-5" stroke="#a6e3a1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <p class="success-text">¡Email actualizado correctamente!</p>
        <RouterLink to="/dashboard" class="btn-primary" style="margin-top:1rem;text-decoration:none">
          Ir al dashboard
        </RouterLink>
      </div>

      <div v-else class="error-box">
        <svg width="36" height="36" viewBox="0 0 24 24" fill="none" style="margin-bottom:0.5rem">
          <circle cx="12" cy="12" r="10" stroke="#f38ba8" stroke-width="2"/>
          <path d="M15 9l-6 6M9 9l6 6" stroke="#f38ba8" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <p>{{ errorMsg }}</p>
        <RouterLink to="/dashboard" class="auth-link">Ir al dashboard</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { usersApi } from '@/api/usersApi'

const route = useRoute()

const loading = ref(true)
const success = ref(false)
const errorMsg = ref('')

onMounted(async () => {
  const token = route.query.token as string
  if (!token) {
    errorMsg.value = 'Link inválido — falta el token.'
    loading.value = false
    return
  }
  try {
    await usersApi.confirmEmail(token)
    success.value = true
  } catch (e: any) {
    errorMsg.value = e?.response?.data?.detail ?? 'Token inválido o expirado.'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #1e1e2e;
  padding: 1rem;
}

.auth-card {
  width: 100%;
  max-width: 380px;
  background: #181825;
  border: 1px solid #313244;
  border-radius: 12px;
  padding: 2rem;
}

.auth-logo {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 1.75rem;
}

.auth-logo-text {
  font-weight: 700;
  font-size: 0.95rem;
  color: #cdd6f4;
}

.status-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  color: #a6adc8;
  font-size: 0.9rem;
  padding: 1rem 0;
}

.success-box,
.error-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 0.5rem 0;
  gap: 0.5rem;
}

.success-text {
  font-size: 0.95rem;
  color: #a6e3a1;
  font-weight: 600;
}

.error-box {
  color: #f38ba8;
  font-size: 0.88rem;
}

.btn-primary {
  display: inline-block;
  padding: 0.6rem 1.25rem;
  background: #cba6f7;
  color: #1e1e2e;
  border-radius: 7px;
  font-weight: 700;
  font-size: 0.88rem;
  cursor: pointer;
  text-align: center;
}

.btn-primary:hover { background: #d4b4ff; }

.auth-link {
  color: #cba6f7;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.85rem;
}

.auth-link:hover { text-decoration: underline; }

.spinner {
  width: 28px;
  height: 28px;
  border: 3px solid #31324460;
  border-top-color: #cba6f7;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }
</style>
