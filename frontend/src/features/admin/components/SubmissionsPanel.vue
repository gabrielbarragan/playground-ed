<template>
  <div class="submissions">
    <div class="sub-toolbar">
      <span class="sub-count">
        {{ filtered.length }} envío(s) pendiente(s)
        <span v-if="hasActiveFilters" class="sub-count-total">de {{ submissions.length }} total</span>
      </span>
      <button class="btn-refresh" @click="load" :disabled="loading">
        <span v-if="loading" class="spinner spinner--sm" />
        <span v-else>↺</span>
        Actualizar
      </button>
    </div>

    <!-- Filters & Sort -->
    <div v-if="submissions.length" class="sub-filters">
      <select v-model="filterCourse" class="sub-select">
        <option value="">Todos los cursos</option>
        <option v-for="c in courseOptions" :key="c.id" :value="c.id">{{ c.name }}</option>
      </select>
      <select v-model="filterChallenge" class="sub-select">
        <option value="">Todos los retos</option>
        <option v-for="ch in challengeOptions" :key="ch.id" :value="ch.id">{{ ch.title }}</option>
      </select>
      <div class="sub-sort">
        <select v-model="sortBy" class="sub-select sub-select--sort">
          <option value="date">Fecha</option>
          <option value="student_name">Estudiante</option>
          <option value="challenge_title">Reto</option>
          <option value="points">Puntos</option>
        </select>
        <button class="btn-sort-dir" @click="toggleSortDir" :title="sortDir === 'asc' ? 'Ascendente' : 'Descendente'">
          {{ sortDir === 'asc' ? '↑' : '↓' }}
        </button>
      </div>
    </div>

    <div v-if="loading && !submissions.length" class="sub-loading">
      <span class="spinner" /> Cargando...
    </div>

    <div v-else-if="!submissions.length" class="sub-empty">
      No hay envíos pendientes de revisión.
    </div>

    <template v-else>
      <div v-if="!filtered.length" class="sub-empty">
        No hay envíos que coincidan con los filtros.
      </div>

      <div v-else class="sub-list">
        <div v-for="s in filtered" :key="s.id" class="sub-card">
          <div class="sub-card-header">
            <div class="sub-info">
              <span class="sub-student">{{ s.user.first_name }} {{ s.user.last_name }}</span>
              <span class="sub-email">{{ s.user.email }}</span>
            </div>
            <div class="sub-challenge-info">
              <span class="sub-challenge-title">{{ s.challenge.title }}</span>
              <span class="diff-badge" :class="`diff--${s.challenge.difficulty}`">
                {{ diffLabel(s.challenge.difficulty) }}
              </span>
              <span class="sub-pts">{{ s.challenge.points }} pts base</span>
              <span class="sub-attempt">intento #{{ s.attempt_number }}</span>
            </div>
            <span class="sub-date">{{ formatDate(s.submitted_at) }}</span>
          </div>

          <div class="sub-code-wrap">
            <pre class="sub-code">{{ s.code }}</pre>
          </div>

          <div v-if="activeId !== s.id" class="sub-actions">
            <button class="btn-approve" @click="startReview(s.id)">Revisar</button>
          </div>

          <div v-else class="sub-review-form">
            <textarea
              v-model="feedback"
              class="feedback-input"
              rows="2"
              placeholder="Comentario al estudiante (opcional)"
            />
            <div class="sub-review-btns">
              <button class="btn-cancel-rev" @click="activeId = null">Cancelar</button>
              <button class="btn-reject" :disabled="acting" @click="reject(s.id)">
                <span v-if="acting === 'reject'" class="spinner spinner--sm" /> Rechazar
              </button>
              <button class="btn-approve-confirm" :disabled="!!acting" @click="approve(s.id)">
                <span v-if="acting === 'approve'" class="spinner spinner--sm" /> Aprobar
              </button>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { challengesApi } from '@/api/challengesApi'
import type { Attempt } from '@/types/challenges'

const submissions = ref<Attempt[]>([])
const loading = ref(false)
const activeId = ref<string | null>(null)
const feedback = ref('')
const acting = ref<'approve' | 'reject' | null>(null)

const filterCourse = ref('')
const filterChallenge = ref('')
const sortBy = ref('date')
const sortDir = ref<'asc' | 'desc'>('asc')

// Reset challenge filter when course changes
watch(filterCourse, () => {
  filterChallenge.value = ''
})

const hasActiveFilters = computed(() => filterCourse.value !== '' || filterChallenge.value !== '')

const courseOptions = computed(() => {
  const map = new Map<string, { id: string; name: string }>()
  for (const s of submissions.value) {
    for (const c of s.challenge.courses ?? []) {
      if (!map.has(c.id)) map.set(c.id, { id: c.id, name: c.name })
    }
  }
  return [...map.values()].sort((a, b) => a.name.localeCompare(b.name))
})

const challengeOptions = computed(() => {
  const map = new Map<string, { id: string; title: string }>()
  for (const s of submissions.value) {
    if (filterCourse.value) {
      const inCourse = (s.challenge.courses ?? []).some((c: any) => c.id === filterCourse.value)
      if (!inCourse) continue
    }
    if (!map.has(s.challenge.id)) {
      map.set(s.challenge.id, { id: s.challenge.id, title: s.challenge.title })
    }
  }
  return [...map.values()].sort((a, b) => a.title.localeCompare(b.title))
})

const filtered = computed(() => {
  let list = submissions.value

  if (filterCourse.value) {
    list = list.filter(s =>
      (s.challenge.courses ?? []).some((c: any) => c.id === filterCourse.value)
    )
  }
  if (filterChallenge.value) {
    list = list.filter(s => s.challenge.id === filterChallenge.value)
  }

  const sortKeys: Record<string, (s: Attempt) => string | number> = {
    student_name: (s) => (s.user.first_name + s.user.last_name).toLowerCase(),
    challenge_title: (s) => s.challenge.title.toLowerCase(),
    points: (s) => s.challenge.points,
    date: (s) => s.submitted_at,
  }
  const keyFn = sortKeys[sortBy.value] ?? sortKeys.date
  const sorted = [...list].sort((a, b) => {
    const va = keyFn(a)
    const vb = keyFn(b)
    if (va < vb) return sortDir.value === 'asc' ? -1 : 1
    if (va > vb) return sortDir.value === 'asc' ? 1 : -1
    return 0
  })

  return sorted
})

function toggleSortDir() {
  sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
}

async function load() {
  loading.value = true
  try {
    const res = await challengesApi.pendingSubmissions()
    submissions.value = res.submissions
  } finally {
    loading.value = false
  }
}

function startReview(id: string) {
  activeId.value = id
  feedback.value = ''
}

async function approve(id: string) {
  acting.value = 'approve'
  try {
    await challengesApi.approveSubmission(id, feedback.value)
    submissions.value = submissions.value.filter(s => s.id !== id)
    activeId.value = null
  } finally {
    acting.value = null
  }
}

async function reject(id: string) {
  acting.value = 'reject'
  try {
    await challengesApi.rejectSubmission(id, feedback.value)
    submissions.value = submissions.value.filter(s => s.id !== id)
    activeId.value = null
  } finally {
    acting.value = null
  }
}

function diffLabel(d: string) {
  return d === 'easy' ? 'Fácil' : d === 'medium' ? 'Media' : 'Difícil'
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleString('es-AR', { dateStyle: 'short', timeStyle: 'short' })
}

onMounted(load)
</script>

<style scoped>
.submissions { display: flex; flex-direction: column; gap: 0; }

.sub-toolbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0.75rem 0; margin-bottom: 0.25rem;
}
.sub-count { font-size: 0.82rem; color: #6c7086; }
.sub-count-total { color: #45475a; font-size: 0.75rem; }
.btn-refresh {
  display: flex; align-items: center; gap: 0.4rem;
  background: transparent; border: 1px solid #313244; border-radius: 6px;
  color: #a6adc8; padding: 0.35rem 0.75rem; font-size: 0.8rem;
  cursor: pointer; font-family: inherit;
}
.btn-refresh:hover:not(:disabled) { border-color: #585b70; }

/* ── Filters ── */
.sub-filters {
  display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;
  padding-bottom: 0.75rem; margin-bottom: 0.75rem;
  border-bottom: 1px solid #313244;
}
.sub-select {
  background: #181825; border: 1px solid #313244; border-radius: 6px;
  color: #cdd6f4; padding: 0.35rem 0.6rem; font-size: 0.78rem;
  font-family: inherit; cursor: pointer; outline: none;
  min-width: 0;
}
.sub-select:focus { border-color: #cba6f7; }
.sub-select option { background: #181825; color: #cdd6f4; }

.sub-sort {
  display: flex; align-items: center; gap: 0.25rem; margin-left: auto;
}
.sub-select--sort { min-width: 100px; }

.btn-sort-dir {
  background: #181825; border: 1px solid #313244; border-radius: 6px;
  color: #cba6f7; width: 30px; height: 30px; font-size: 0.9rem;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  font-family: inherit; padding: 0;
}
.btn-sort-dir:hover { border-color: #cba6f7; }

/* ── List ── */
.sub-loading, .sub-empty {
  display: flex; align-items: center; gap: 0.75rem;
  color: #6c7086; font-size: 0.85rem; padding: 2rem 0; justify-content: center;
}

.sub-list { display: flex; flex-direction: column; gap: 1rem; }

.sub-card {
  background: #181825; border: 1px solid #313244; border-radius: 10px; overflow: hidden;
}
.sub-card-header {
  display: flex; align-items: flex-start; gap: 1rem; flex-wrap: wrap;
  padding: 0.85rem 1rem; border-bottom: 1px solid #313244;
}
.sub-info { display: flex; flex-direction: column; gap: 0.15rem; min-width: 160px; }
.sub-student { font-size: 0.88rem; font-weight: 700; color: #cdd6f4; }
.sub-email { font-size: 0.72rem; color: #6c7086; }
.sub-challenge-info { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; flex: 1; }
.sub-challenge-title { font-size: 0.85rem; color: #cba6f7; font-weight: 600; }
.diff-badge {
  font-size: 0.65rem; padding: 0.1rem 0.45rem; border-radius: 4px; font-weight: 700;
}
.diff--easy { background: #1e3a1e; color: #a6e3a1; }
.diff--medium { background: #3a2a1e; color: #fab387; }
.diff--hard { background: #3a1e1e; color: #f38ba8; }
.sub-pts { font-size: 0.75rem; color: #6c7086; }
.sub-attempt { font-size: 0.72rem; color: #45475a; }
.sub-date { font-size: 0.72rem; color: #45475a; margin-left: auto; }

.sub-code-wrap { max-height: 240px; overflow-y: auto; background: #11111b; }
.sub-code {
  margin: 0; padding: 1rem; font-family: 'JetBrains Mono', monospace;
  font-size: 0.78rem; color: #cdd6f4; white-space: pre-wrap; word-break: break-all;
}
.sub-actions { padding: 0.75rem 1rem; display: flex; justify-content: flex-end; }
.btn-approve {
  background: #313244; border: none; border-radius: 6px; color: #cdd6f4;
  padding: 0.4rem 1rem; font-size: 0.82rem; cursor: pointer; font-family: inherit;
}
.btn-approve:hover { background: #45475a; }

.sub-review-form { padding: 0.75rem 1rem; border-top: 1px solid #313244; display: flex; flex-direction: column; gap: 0.5rem; }
.feedback-input {
  background: #11111b; border: 1px solid #313244; border-radius: 6px;
  color: #cdd6f4; padding: 0.5rem 0.75rem; font-family: inherit; font-size: 0.82rem;
  resize: vertical; outline: none; width: 100%; box-sizing: border-box;
}
.feedback-input:focus { border-color: #cba6f7; }
.sub-review-btns { display: flex; gap: 0.5rem; justify-content: flex-end; align-items: center; }
.btn-cancel-rev {
  background: transparent; border: 1px solid #313244; border-radius: 6px;
  color: #6c7086; padding: 0.4rem 0.9rem; font-size: 0.82rem; cursor: pointer; font-family: inherit;
}
.btn-reject {
  background: #3a1e1e; border: 1px solid #f38ba840; border-radius: 6px;
  color: #f38ba8; padding: 0.4rem 1rem; font-size: 0.82rem; cursor: pointer;
  font-family: inherit; display: flex; align-items: center; gap: 0.4rem;
}
.btn-reject:hover:not(:disabled) { background: #4a2020; }
.btn-reject:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-approve-confirm {
  background: #1e3a1e; border: 1px solid #a6e3a140; border-radius: 6px;
  color: #a6e3a1; padding: 0.4rem 1rem; font-size: 0.82rem; cursor: pointer;
  font-family: inherit; display: flex; align-items: center; gap: 0.4rem;
}
.btn-approve-confirm:hover:not(:disabled) { background: #254a25; }
.btn-approve-confirm:disabled { opacity: 0.5; cursor: not-allowed; }

.spinner {
  display: inline-block; width: 14px; height: 14px;
  border: 2px solid #45475a; border-top-color: #cba6f7;
  border-radius: 50%; animation: spin 0.7s linear infinite;
}
.spinner--sm { width: 11px; height: 11px; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
