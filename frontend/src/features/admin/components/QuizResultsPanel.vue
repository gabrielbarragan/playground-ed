<template>
  <div class="results-panel">
    <div class="rp-header">
      <h3 class="rp-title">Resultados — {{ quizTitle }}</h3>
      <button class="rp-close" @click="$emit('close')">✕</button>
    </div>

    <div v-if="loading" class="rp-loading">
      <span class="spinner" /> Cargando resultados...
    </div>

    <div v-else-if="!results.length" class="rp-empty">
      Ningún estudiante ha completado este quiz.
    </div>

    <div v-else class="rp-table-wrap">
      <table class="rp-table">
        <thead>
          <tr>
            <th>Estudiante</th>
            <th>Email</th>
            <th>Resultado</th>
            <th>Estado</th>
            <th>Puntos</th>
            <th>Fecha</th>
            <th>Acción</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in results" :key="r.id">
            <td class="cell-name">{{ r.user.first_name }} {{ r.user.last_name }}</td>
            <td class="cell-email">{{ r.user.email }}</td>
            <td class="cell-score">{{ r.correct_count }} / {{ r.total_questions }}</td>
            <td>
              <span class="status-badge" :class="r.passed ? 'status--pass' : 'status--fail'">
                {{ r.passed ? 'Aprobado' : 'No aprobado' }}
              </span>
            </td>
            <td class="cell-pts">+{{ r.points_earned }}</td>
            <td class="cell-date">{{ formatDate(r.submitted_at) }}</td>
            <td>
              <button
                class="btn-reset"
                :disabled="resettingId === r.user.id"
                @click="handleReset(r)"
              >
                <span v-if="resettingId === r.user.id" class="spinner spinner--sm" />
                Resetear
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { quizzesApi } from '@/api/quizzesApi'
import type { QuizStudentResult } from '@/types/quizzes'

const props = defineProps<{ quizId: string; quizTitle: string }>()
defineEmits<{ close: [] }>()

const results = ref<QuizStudentResult[]>([])
const loading = ref(true)
const resettingId = ref<string | null>(null)

async function load() {
  loading.value = true
  try {
    const res = await quizzesApi.getResults(props.quizId)
    results.value = res.results
  } finally {
    loading.value = false
  }
}

async function handleReset(r: QuizStudentResult) {
  if (!confirm(`¿Resetear el intento de ${r.user.first_name}? Los puntos acreditados no se revertirán.`)) return
  resettingId.value = r.user.id
  try {
    await quizzesApi.resetAttempt(props.quizId, r.user.id)
    results.value = results.value.filter(x => x.id !== r.id)
  } finally {
    resettingId.value = null
  }
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('es-AR', { day: '2-digit', month: 'short', year: 'numeric' })
}

onMounted(load)
</script>

<style scoped>
.results-panel {
  background: #181825;
  border: 1px solid #313244;
  border-radius: 10px;
  overflow: hidden;
}

.rp-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #313244;
}

.rp-title {
  font-size: 0.88rem;
  font-weight: 700;
  color: #cdd6f4;
  margin: 0;
}

.rp-close {
  background: transparent;
  border: none;
  color: #6c7086;
  cursor: pointer;
  font-size: 0.9rem;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  transition: color 0.15s;
}
.rp-close:hover { color: #f38ba8; }

.rp-loading,
.rp-empty {
  padding: 2rem;
  text-align: center;
  font-size: 0.82rem;
  color: #45475a;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
}

.rp-table-wrap { overflow-x: auto; }

.rp-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.82rem;
}

.rp-table th {
  text-align: left;
  padding: 0.5rem 0.75rem;
  font-size: 0.7rem;
  color: #45475a;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  border-bottom: 1px solid #313244;
  white-space: nowrap;
}

.rp-table td {
  padding: 0.65rem 0.75rem;
  border-bottom: 1px solid #1e1e2e;
  color: #cdd6f4;
  vertical-align: middle;
}

.rp-table tr:last-child td { border-bottom: none; }
.rp-table tbody tr:hover td { background: #1e1e2e; }

.cell-name { font-weight: 500; white-space: nowrap; }
.cell-email { color: #6c7086; font-size: 0.78rem; }
.cell-score { font-weight: 600; color: #a6adc8; }
.cell-pts { font-weight: 600; color: #f9e2af; }
.cell-date { font-size: 0.75rem; color: #6c7086; white-space: nowrap; }

.status-badge {
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  white-space: nowrap;
}
.status--pass { background: #a6e3a120; color: #a6e3a1; }
.status--fail { background: #f38ba820; color: #f38ba8; }

.btn-reset {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.3rem 0.7rem;
  background: transparent;
  border: 1px solid #313244;
  border-radius: 5px;
  color: #6c7086;
  font-family: inherit;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: border-color 0.15s, color 0.15s;
  white-space: nowrap;
}
.btn-reset:hover:not(:disabled) { border-color: #f38ba8; color: #f38ba8; }
.btn-reset:disabled { opacity: 0.4; cursor: not-allowed; }

.spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid #31324480;
  border-top-color: #cba6f7;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  vertical-align: middle;
}
.spinner--sm { width: 10px; height: 10px; border-width: 1.5px; }

@keyframes spin { to { transform: rotate(360deg); } }
</style>