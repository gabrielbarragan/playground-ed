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

      <h1 class="auth-title">Iniciar Sesión</h1>

      <form @submit.prevent="handleSubmit" novalidate>
        <div class="form-group">
          <label class="form-label">Correo electrónico</label>
          <input
            v-model="email"
            type="email"
            class="form-input"
            :class="{ 'form-input--error': !!error }"
            placeholder="usuario@ejemplo.com"
            autocomplete="email"
            required
          />
        </div>

        <div class="form-group">
          <label class="form-label">Contraseña</label>
          <input
            v-model="password"
            type="password"
            class="form-input"
            :class="{ 'form-input--error': !!error }"
            placeholder="••••••••"
            autocomplete="current-password"
            required
          />
        </div>

        <p v-if="error" class="form-error">{{ error }}</p>

        <button type="submit" class="btn-submit" :disabled="loading">
          <span v-if="loading" class="spinner" />
          {{ loading ? 'Ingresando...' : 'Ingresar' }}
        </button>
      </form>

      <p class="auth-footer">
        ¿No tenés cuenta?
        <RouterLink to="/register" class="auth-link">Registrate</RouterLink>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/useAuthStore'

const router = useRouter()
const auth = useAuthStore()

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function handleSubmit() {
  error.value = ''
  loading.value = true
  try {
    await auth.login({ email: email.value, password: password.value })
    router.push('/')
  } catch (e: any) {
    error.value = e?.message?.includes('401') || e?.statusCode === 401
      ? 'Correo o contraseña incorrectos'
      : (e?.message ?? 'Error al iniciar sesión')
  } finally {
    loading.value = false
  }
}
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
  max-width: 400px;
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

.auth-title {
  font-size: 1.35rem;
  font-weight: 700;
  color: #cdd6f4;
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-label {
  display: block;
  font-size: 0.78rem;
  color: #a6adc8;
  margin-bottom: 0.4rem;
  font-weight: 500;
}

.form-input {
  width: 100%;
  padding: 0.6rem 0.85rem;
  background: #1e1e2e;
  border: 1px solid #313244;
  border-radius: 7px;
  color: #cdd6f4;
  font-family: inherit;
  font-size: 0.9rem;
  outline: none;
  transition: border-color 0.15s;
  box-sizing: border-box;
}

.form-input::placeholder { color: #45475a; }

.form-input:focus {
  border-color: #cba6f7;
}

.form-input--error {
  border-color: #f38ba8;
}

.form-error {
  font-size: 0.78rem;
  color: #f38ba8;
  margin-bottom: 0.75rem;
  padding: 0.5rem 0.75rem;
  background: #f38ba810;
  border: 1px solid #f38ba830;
  border-radius: 6px;
}

.btn-submit {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.65rem;
  margin-top: 0.5rem;
  background: #cba6f7;
  color: #1e1e2e;
  border: none;
  border-radius: 7px;
  font-weight: 700;
  font-size: 0.9rem;
  font-family: inherit;
  cursor: pointer;
  transition: background 0.15s, transform 0.1s;
}

.btn-submit:hover:not(:disabled) {
  background: #d4b4ff;
  transform: translateY(-1px);
}

.btn-submit:active:not(:disabled) {
  transform: translateY(0);
}

.btn-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.spinner {
  width: 13px;
  height: 13px;
  border: 2px solid #1e1e2e60;
  border-top-color: #1e1e2e;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.auth-footer {
  margin-top: 1.25rem;
  text-align: center;
  font-size: 0.82rem;
  color: #6c7086;
}

.auth-link {
  color: #cba6f7;
  text-decoration: none;
  font-weight: 600;
}

.auth-link:hover {
  text-decoration: underline;
}
</style>