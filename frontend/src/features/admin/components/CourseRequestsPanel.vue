<template>
  <div class="cr-panel">
    <div class="cr-toolbar">
      <span class="cr-toolbar-title">
        Solicitudes de cambio de curso
        <span class="cr-count">{{ requests.length }}</span>
      </span>
      <button class="cr-btn-refresh" :disabled="loading" @click="load">
        {{ loading ? 'Cargando...' : 'Actualizar' }}
      </button>
    </div>

    <div v-if="loading && !requests.length" class="cr-loading">Cargando solicitudes...</div>

    <div v-else-if="!requests.length" class="cr-empty">
      No hay solicitudes pendientes.
    </div>

    <div v-else class="cr-list">
      <div v-for="req in requests" :key="req.id" class="cr-card">
        <div class="cr-card-header">
          <span class="cr-student-name">{{ req.user.first_name }} {{ req.user.last_name }}</span>
          <span class="cr-student-email">{{ req.user.email }}</span>
        </div>
        <div class="cr-card-body">
          <div class="cr-course-flow">
            <span class="cr-course-badge">{{ req.from_course.code }}</span>
            <span class="cr-arrow">→</span>
            <span class="cr-course-badge cr-course-badge--target">{{ req.to_course.code }}</span>
          </div>
          <div class="cr-course-names">
            {{ req.from_course.name }} → {{ req.to_course.name }}
          </div>
          <p v-if="req.reason" class="cr-reason">{{ req.reason }}</p>
          <span class="cr-date">{{ formatDate(req.created_at) }}</span>
        </div>
        <div class="cr-card-actions">
          <button
            class="cr-btn cr-btn--approve"
            :disabled="resolving === req.id"
            @click="resolve(req.id, 'approve')"
          >
            Aprobar
          </button>
          <button
            class="cr-btn cr-btn--reject"
            :disabled="resolving === req.id"
            @click="startReject(req.id)"
          >
            Rechazar
          </button>
        </div>
        <div v-if="rejectingId === req.id" class="cr-reject-form">
          <input
            v-model="rejectReason"
            class="cr-reject-input"
            placeholder="Razón del rechazo (opcional)"
            maxlength="500"
            @keyup.enter="resolve(req.id, 'reject')"
            @keyup.escape="rejectingId = null"
          />
          <button class="cr-btn cr-btn--reject-confirm" @click="resolve(req.id, 'reject')">Confirmar</button>
          <button class="cr-btn cr-btn--cancel" @click="rejectingId = null">Cancelar</button>
        </div>
      </div>
    </div>

    <p v-if="error" class="cr-error">{{ error }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { courseRequestsApi, type CourseChangeRequest } from '@/api/courseRequestsApi'

const requests = ref<CourseChangeRequest[]>([])
const loading = ref(false)
const resolving = ref<string | null>(null)
const rejectingId = ref<string | null>(null)
const rejectReason = ref('')
const error = ref('')

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('es-AR', {
    day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit',
  })
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const res = await courseRequestsApi.listPendingRequests()
    requests.value = res.requests
  } catch {
    error.value = 'Error al cargar solicitudes'
  } finally {
    loading.value = false
  }
}

function startReject(id: string) {
  rejectingId.value = id
  rejectReason.value = ''
}

async function resolve(id: string, action: 'approve' | 'reject') {
  resolving.value = id
  error.value = ''
  try {
    await courseRequestsApi.resolveRequest(id, action, action === 'reject' ? rejectReason.value : '')
    requests.value = requests.value.filter(r => r.id !== id)
    rejectingId.value = null
  } catch (e: any) {
    error.value = e?.response?.data?.detail ?? 'Error al resolver solicitud'
  } finally {
    resolving.value = null
  }
}

onMounted(load)
</script>

<style scoped>
.cr-panel {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.cr-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.cr-toolbar-title {
  font-size: 0.9rem;
  font-weight: 700;
  color: #a6adc8;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.cr-count {
  font-size: 0.72rem;
  background: #313244;
  color: #6c7086;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-weight: 400;
}

.cr-btn-refresh {
  padding: 0.35rem 0.75rem;
  background: #313244;
  border: none;
  border-radius: 6px;
  color: #cdd6f4;
  font-family: inherit;
  font-size: 0.78rem;
  cursor: pointer;
}
.cr-btn-refresh:hover:not(:disabled) { background: #45475a; }
.cr-btn-refresh:disabled { opacity: 0.5; cursor: not-allowed; }

.cr-loading,
.cr-empty {
  color: #6c7086;
  font-size: 0.85rem;
  text-align: center;
  padding: 2rem 0;
}

.cr-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.cr-card {
  background: #181825;
  border: 1px solid #313244;
  border-radius: 10px;
  padding: 1rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.cr-card-header {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
}

.cr-student-name {
  font-size: 0.9rem;
  font-weight: 600;
  color: #cdd6f4;
}

.cr-student-email {
  font-size: 0.75rem;
  color: #6c7086;
}

.cr-card-body {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.cr-course-flow {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.cr-course-badge {
  font-size: 0.7rem;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  background: #313244;
  color: #cba6f7;
  font-weight: 700;
  font-family: monospace;
}

.cr-course-badge--target {
  background: #2a1f3d;
  border: 1px solid #cba6f750;
}

.cr-arrow {
  color: #6c7086;
  font-size: 0.85rem;
}

.cr-course-names {
  font-size: 0.78rem;
  color: #a6adc8;
}

.cr-reason {
  font-size: 0.78rem;
  color: #a6adc8;
  font-style: italic;
  margin: 0;
  padding: 0.3rem 0.5rem;
  background: #1e1e2e;
  border-radius: 4px;
}

.cr-date {
  font-size: 0.7rem;
  color: #585b70;
}

.cr-card-actions {
  display: flex;
  gap: 0.5rem;
}

.cr-btn {
  padding: 0.35rem 0.75rem;
  border: 1px solid transparent;
  border-radius: 6px;
  font-family: inherit;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s, opacity 0.15s;
}
.cr-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.cr-btn--approve {
  background: #a6e3a115;
  border-color: #a6e3a140;
  color: #a6e3a1;
}
.cr-btn--approve:hover:not(:disabled) { background: #a6e3a125; }

.cr-btn--reject {
  background: #f38ba815;
  border-color: #f38ba840;
  color: #f38ba8;
}
.cr-btn--reject:hover:not(:disabled) { background: #f38ba825; }

.cr-reject-form {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.cr-reject-input {
  flex: 1;
  min-width: 180px;
  padding: 0.35rem 0.65rem;
  background: #1e1e2e;
  border: 1px solid #313244;
  border-radius: 6px;
  color: #cdd6f4;
  font-family: inherit;
  font-size: 0.82rem;
  outline: none;
}
.cr-reject-input:focus { border-color: #cba6f7; }

.cr-btn--reject-confirm {
  background: #f38ba8;
  color: #1e1e2e;
  font-weight: 700;
}

.cr-btn--cancel {
  background: #313244;
  color: #cdd6f4;
}
.cr-btn--cancel:hover { background: #45475a; }

.cr-error {
  color: #f38ba8;
  font-size: 0.82rem;
  margin: 0;
}
</style>
