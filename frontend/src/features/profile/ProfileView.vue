<template>
  <div class="profile-page">
    <!-- Header -->
    <header class="profile-header">
      <div class="header-left">
        <RouterLink to="/" class="back-link">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
            <path d="M19 12H5M12 5l-7 7 7 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          Playground
        </RouterLink>
        <span class="profile-title">Mi Perfil</span>
      </div>
      <div class="header-right">
        <span class="user-chip">{{ auth.user?.email }}</span>
      </div>
    </header>

    <main class="profile-body">

      <!-- Info actual -->
      <section class="section">
        <h2 class="section-title">Información de cuenta</h2>
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">Nombre</span>
            <span class="info-value">{{ auth.user?.first_name }} {{ auth.user?.last_name }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Email</span>
            <span class="info-value">{{ auth.user?.email }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Curso</span>
            <span class="info-value">{{ auth.user?.course?.name ?? '—' }}</span>
          </div>
        </div>
      </section>

      <!-- Cambio de email -->
      <section class="section">
        <h2 class="section-title">Cambiar email</h2>
        <p class="section-desc">
          Ingresá el nuevo correo. Te enviaremos un link de confirmación a esa dirección — el cambio se aplica solo después de confirmarlo.
        </p>

        <form v-if="!emailSent" class="email-form" @submit.prevent="handleEmailChange" novalidate>
          <div class="form-group">
            <label class="form-label">Nuevo correo electrónico</label>
            <input
              v-model="newEmail"
              type="email"
              class="form-input"
              :class="{ 'form-input--error': !!emailError }"
              placeholder="nuevo@correo.com"
              autocomplete="email"
              required
            />
          </div>
          <p v-if="emailError" class="form-error">{{ emailError }}</p>
          <button type="submit" class="btn-primary" :disabled="emailLoading">
            <span v-if="emailLoading" class="spinner" />
            {{ emailLoading ? 'Enviando...' : 'Solicitar cambio' }}
          </button>
        </form>

        <div v-else class="success-box">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="10" stroke="#a6e3a1" stroke-width="2"/>
            <path d="M8 12l3 3 5-5" stroke="#a6e3a1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span>Te enviamos un link de confirmación a <strong>{{ newEmail }}</strong>.<br>
          Revisá tu bandeja de entrada (y spam).</span>
          <button class="btn-ghost" @click="emailSent = false">Solicitar con otro correo</button>
        </div>
      </section>

    </main>
    <AppFooter />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import AppFooter from '@/components/AppFooter.vue'
import { useAuthStore } from '@/stores/useAuthStore'
import { usersApi } from '@/api/usersApi'

const auth = useAuthStore()

const newEmail = ref('')
const emailLoading = ref(false)
const emailError = ref('')
const emailSent = ref(false)

async function handleEmailChange() {
  emailError.value = ''
  if (!newEmail.value) return
  if (newEmail.value === auth.user?.email) {
    emailError.value = 'El nuevo correo es igual al actual'
    return
  }
  emailLoading.value = true
  try {
    await usersApi.changeMyEmail(newEmail.value)
    emailSent.value = true
  } catch (e: any) {
    emailError.value = e?.response?.data?.detail ?? 'Error al solicitar el cambio de email'
  } finally {
    emailLoading.value = false
  }
}
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background: #1e1e2e;
  color: #cdd6f4;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  display: flex;
  flex-direction: column;
}

.profile-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.5rem;
  height: 48px;
  background: #181825;
  border-bottom: 1px solid #313244;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.back-link {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.78rem;
  color: #6c7086;
  text-decoration: none;
  transition: color 0.15s;
}
.back-link:hover { color: #a6adc8; }

.profile-title {
  font-size: 0.9rem;
  font-weight: 700;
  color: #cdd6f4;
}

.user-chip {
  font-size: 0.75rem;
  color: #a6adc8;
  background: #313244;
  padding: 0.25rem 0.65rem;
  border-radius: 20px;
}

.profile-body {
  max-width: 600px;
  width: 100%;
  margin: 2rem auto;
  padding: 0 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.section {
  background: #181825;
  border: 1px solid #313244;
  border-radius: 10px;
  padding: 1.5rem;
}

.section-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #cba6f7;
  margin-bottom: 1rem;
}

.section-desc {
  font-size: 0.82rem;
  color: #a6adc8;
  margin-bottom: 1.25rem;
  line-height: 1.5;
}

.info-grid {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.info-item {
  display: flex;
  gap: 1rem;
  align-items: baseline;
}

.info-label {
  font-size: 0.75rem;
  color: #6c7086;
  min-width: 60px;
}

.info-value {
  font-size: 0.88rem;
  color: #cdd6f4;
}

.email-form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.form-group { display: flex; flex-direction: column; gap: 0.35rem; }

.form-label {
  font-size: 0.78rem;
  color: #a6adc8;
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
.form-input:focus { border-color: #cba6f7; }
.form-input--error { border-color: #f38ba8; }

.form-error {
  font-size: 0.78rem;
  color: #f38ba8;
  padding: 0.4rem 0.7rem;
  background: #f38ba810;
  border: 1px solid #f38ba830;
  border-radius: 6px;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.55rem 1.25rem;
  background: #cba6f7;
  color: #1e1e2e;
  border: none;
  border-radius: 7px;
  font-weight: 700;
  font-size: 0.85rem;
  font-family: inherit;
  cursor: pointer;
  transition: background 0.15s;
  align-self: flex-start;
}

.btn-primary:hover:not(:disabled) { background: #d4b4ff; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-ghost {
  font-size: 0.78rem;
  color: #cba6f7;
  background: none;
  border: none;
  cursor: pointer;
  font-family: inherit;
  text-decoration: underline;
  padding: 0;
}

.success-box {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.85rem 1rem;
  background: #a6e3a110;
  border: 1px solid #a6e3a130;
  border-radius: 8px;
  font-size: 0.85rem;
  color: #a6adc8;
  flex-wrap: wrap;
}

.success-box strong { color: #cdd6f4; }

.spinner {
  width: 13px;
  height: 13px;
  border: 2px solid #1e1e2e60;
  border-top-color: #1e1e2e;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
}

@keyframes spin { to { transform: rotate(360deg); } }
</style>
