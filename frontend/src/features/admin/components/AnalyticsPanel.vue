<template>
  <div class="analytics">

    <!-- ── Filtros ─────────────────────────────────────────────────────────── -->
    <div class="analytics-filters">
      <div class="filter-group">
        <label class="filter-label">Curso</label>
        <select v-model="selectedCourseId" class="filter-select" @change="load">
          <option value="">Todos los cursos</option>
          <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
      </div>

      <div class="filter-group">
        <label class="filter-label">Reto</label>
        <select v-model="selectedChallengeId" class="filter-select" @change="onChallengeChange">
          <option value="">Todos los retos</option>
          <option v-for="c in challenges" :key="c.id" :value="c.id">{{ c.title }}</option>
        </select>
      </div>

      <div class="filter-group">
        <label class="filter-label">Período</label>
        <select v-model="days" class="filter-select" @change="load">
          <option :value="7">Últimos 7 días</option>
          <option :value="14">Últimos 14 días</option>
          <option :value="30">Últimos 30 días</option>
        </select>
      </div>

      <div class="filter-summary" v-if="heatmap">
        <span class="fs-total">{{ heatmap.total_errors }}</span>
        <span class="fs-label">errores en el período</span>
      </div>
    </div>

    <div v-if="loading" class="analytics-loading">
      <span class="spinner" /> Cargando analítica...
    </div>

    <template v-else-if="heatmap">

      <!-- ── Panel 1: Tipos de error ──────────────────────────────────────── -->
      <section class="analytics-section">
        <h3 class="analytics-section-title">Tipos de error más frecuentes</h3>
        <div v-if="!heatmap.by_error_type.length" class="analytics-empty">
          Sin errores en este período.
        </div>
        <div v-else class="hbar-list">
          <div
            v-for="item in heatmap.by_error_type.slice(0, 8)"
            :key="item.type"
            class="hbar-row"
          >
            <span class="hbar-label">{{ item.type }}</span>
            <div class="hbar-track">
              <div
                class="hbar-fill hbar-fill--type"
                :style="{ width: barWidth(item.count, heatmap!.by_error_type[0].count) + '%' }"
              />
            </div>
            <span class="hbar-count">{{ item.count }}</span>
          </div>
        </div>
      </section>

      <!-- ── Panel 2: Conceptos ───────────────────────────────────────────── -->
      <section class="analytics-section">
        <h3 class="analytics-section-title">Conceptos con más errores</h3>
        <div v-if="!heatmap.by_concept.length" class="analytics-empty">
          Sin datos de conceptos.
        </div>
        <div v-else class="hbar-list">
          <div
            v-for="item in heatmap.by_concept.slice(0, 10)"
            :key="item.concept"
            class="hbar-row"
          >
            <span class="hbar-label">{{ CONCEPT_LABELS[item.concept] ?? item.concept }}</span>
            <div class="hbar-track">
              <div
                class="hbar-fill"
                :class="conceptFillClass(item.pct_users)"
                :style="{ width: barWidth(item.error_count, heatmap!.by_concept[0].error_count) + '%' }"
                :title="`${item.error_count} errores · ${item.users_affected} alumnos (${item.pct_users}%)`"
              />
            </div>
            <span class="hbar-count">{{ item.error_count }}</span>
            <span class="hbar-users">{{ item.users_affected }} alumnos</span>
          </div>
        </div>
      </section>

      <!-- ── Panel 3: Heatmap por línea (solo con reto seleccionado) ──────── -->
      <section v-if="selectedChallengeId && challengeErrors" class="analytics-section">
        <h3 class="analytics-section-title">
          Mapa de calor por línea
          <span class="section-subtitle">— starter code del reto</span>
        </h3>
        <div v-if="loadingChallengeErrors" class="analytics-loading">
          <span class="spinner" />
        </div>
        <div v-else-if="!challengeErrors.by_line.length" class="analytics-empty">
          Sin errores por línea para este reto.
        </div>
        <div v-else class="code-heatmap">
          <div
            v-for="(line, idx) in starterCodeLines"
            :key="idx"
            class="code-line"
            :class="lineHeatClass(idx + 1)"
            :title="lineTooltip(idx + 1)"
          >
            <span class="code-lineno">{{ idx + 1 }}</span>
            <pre class="code-text">{{ line }}</pre>
            <span v-if="lineErrorCount(idx + 1)" class="code-badge">
              {{ lineErrorCount(idx + 1) }}
            </span>
          </div>
        </div>
      </section>

      <!-- ── Panel 4: Historial reciente ──────────────────────────────────── -->
      <section class="analytics-section">
        <h3 class="analytics-section-title">Historial reciente</h3>

        <!-- Filtro de reto para historial (cuando no hay reto global seleccionado) -->
        <div v-if="!selectedChallengeId" class="filter-group filter-group--inline">
          <label class="filter-label">Reto</label>
          <select v-model="historyFilterChallengeId" class="filter-select" @change="loadRecentHistory">
            <option value="">Todos</option>
            <option v-for="c in challenges" :key="c.id" :value="c.id">{{ c.title }}</option>
          </select>
        </div>

        <div v-if="loadingHistory" class="analytics-loading"><span class="spinner" /></div>
        <div v-else-if="!recentErrors.length" class="analytics-empty">
          Sin errores recientes.
        </div>
        <table v-else class="analytics-table">
          <thead>
            <tr>
              <th>Alumno</th>
              <th>Reto</th>
              <th>Error</th>
              <th>Línea</th>
              <th>Hace</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="ev in recentErrors" :key="ev.id">
              <td>{{ ev.student }}</td>
              <td>{{ ev.challenge ?? '—' }}</td>
              <td><span class="error-type-badge">{{ ev.error_type }}</span></td>
              <td>{{ ev.error_line ?? '—' }}</td>
              <td>{{ timeAgo(ev.created_at) }}</td>
            </tr>
          </tbody>
        </table>
      </section>

    </template>

    <div v-else class="analytics-empty analytics-empty--top">
      Sin datos. Ejecuta código con errores para empezar a ver analítica.
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import {
  analyticsApi,
  type ErrorHeatmapResponse,
  type ChallengeErrorsResponse,
  type RecentErrorEvent,
} from '@/api/analyticsApi'
import type { Challenge } from '@/types/challenges'
import type { AdminCourse } from '@/api/adminApi'

const props = defineProps<{
  challenges: Challenge[]
  courses: AdminCourse[]
}>()

// ── Filtros ──────────────────────────────────────────────────────────────────
const selectedCourseId = ref('')
const selectedChallengeId = ref('')
const historyFilterChallengeId = ref('')
const days = ref(7)

// ── Estado ───────────────────────────────────────────────────────────────────
const loading = ref(false)
const heatmap = ref<ErrorHeatmapResponse | null>(null)

const loadingChallengeErrors = ref(false)
const challengeErrors = ref<ChallengeErrorsResponse | null>(null)

const loadingHistory = ref(false)
const recentErrors = ref<RecentErrorEvent[]>([])

// ── Computed helpers ──────────────────────────────────────────────────────────
const selectedChallenge = computed(() =>
  props.challenges.find(c => c.id === selectedChallengeId.value) ?? null,
)

const starterCodeLines = computed(() =>
  (selectedChallenge.value?.starter_code ?? '').split('\n'),
)

const lineMap = computed(() => {
  const m = new Map<number, { error_count: number; top_error: string; users_affected: number }>()
  for (const l of (challengeErrors.value?.by_line ?? [])) {
    m.set(l.line, l)
  }
  return m
})

const maxLineErrors = computed(() => {
  const lines = challengeErrors.value?.by_line ?? []
  return lines.length ? Math.max(...lines.map(l => l.error_count)) : 1
})

// ── Etiquetas de conceptos ────────────────────────────────────────────────────
const CONCEPT_LABELS: Record<string, string> = {
  loop_for: 'Bucle for',
  loop_while: 'Bucle while',
  nested_loop: 'Bucle anidado',
  list_comp: 'List comprehension',
  try_except: 'Try/except',
  recursion: 'Recursión',
  class: 'Clase',
  lambda: 'Lambda',
  dict_comp: 'Dict comprehension',
  generator: 'Generator',
  decorator: 'Decorador',
}

// ── Carga de datos ────────────────────────────────────────────────────────────
async function load() {
  loading.value = true
  try {
    heatmap.value = await analyticsApi.getErrorHeatmap({
      course_id: selectedCourseId.value || undefined,
      challenge_id: selectedChallengeId.value || undefined,
      days: days.value,
    })
  } finally {
    loading.value = false
  }
  await loadRecentHistory()
}

async function loadChallengeErrors() {
  if (!selectedChallengeId.value) {
    challengeErrors.value = null
    return
  }
  loadingChallengeErrors.value = true
  try {
    challengeErrors.value = await analyticsApi.getChallengeErrors(selectedChallengeId.value)
  } finally {
    loadingChallengeErrors.value = false
  }
}

async function loadRecentHistory() {
  loadingHistory.value = true
  const challengeIdForHistory = selectedChallengeId.value || historyFilterChallengeId.value
  try {
    const res = await analyticsApi.getErrorHeatmap({
      course_id: selectedCourseId.value || undefined,
      challenge_id: challengeIdForHistory || undefined,
      days: days.value,
    })
    // Reutilizamos el heatmap full para extraer historial reciente
    // El endpoint de challenges/{id}/errors expone recent[] directamente
    if (selectedChallengeId.value && challengeErrors.value) {
      recentErrors.value = challengeErrors.value.recent
    } else {
      // Para historial sin reto específico, pedimos el endpoint de challenge errors si hay filtro
      if (challengeIdForHistory) {
        const detail = await analyticsApi.getChallengeErrors(challengeIdForHistory)
        recentErrors.value = detail.recent
      } else {
        recentErrors.value = []
      }
    }
  } finally {
    loadingHistory.value = false
  }
}

async function onChallengeChange() {
  await Promise.all([load(), loadChallengeErrors()])
  if (selectedChallengeId.value && challengeErrors.value) {
    recentErrors.value = challengeErrors.value.recent
    loadingHistory.value = false
  }
}

// ── Helpers de UI ─────────────────────────────────────────────────────────────
function barWidth(value: number, max: number): number {
  return max ? Math.round((value / max) * 100) : 0
}

function conceptFillClass(pctUsers: number): string {
  if (pctUsers >= 50) return 'hbar-fill--danger'
  if (pctUsers >= 25) return 'hbar-fill--warn'
  return 'hbar-fill--ok'
}

function lineErrorCount(lineNum: number): number {
  return lineMap.value.get(lineNum)?.error_count ?? 0
}

function lineHeatClass(lineNum: number): string {
  const count = lineErrorCount(lineNum)
  if (!count) return ''
  const ratio = count / maxLineErrors.value
  if (ratio >= 0.7) return 'line-heat--high'
  if (ratio >= 0.3) return 'line-heat--mid'
  return 'line-heat--low'
}

function lineTooltip(lineNum: number): string {
  const info = lineMap.value.get(lineNum)
  if (!info) return ''
  return `${info.error_count} errores · Tipo más común: ${info.top_error} · ${info.users_affected} alumnos`
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime()
  const mins = Math.floor(diff / 60_000)
  if (mins < 60) return `hace ${mins}m`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `hace ${hrs}h`
  return `hace ${Math.floor(hrs / 24)}d`
}

onMounted(load)
</script>

<style scoped>
/* ── Layout ──────────────────────────────────────────────────────────────── */
.analytics { display: flex; flex-direction: column; gap: 1.5rem; }

.analytics-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: flex-end;
  padding: 1rem;
  background: #181825;
  border: 1px solid #313244;
  border-radius: 8px;
}

.filter-group { display: flex; flex-direction: column; gap: .3rem; }
.filter-group--inline { flex-direction: row; align-items: center; gap: .5rem; margin-bottom: .75rem; }
.filter-label { font-size: .7rem; color: #a6adc8; text-transform: uppercase; letter-spacing: .05em; }
.filter-select {
  background: #1e1e2e; border: 1px solid #313244; border-radius: 6px;
  color: #cdd6f4; padding: .4rem .7rem; font-size: .85rem; min-width: 160px;
}
.filter-select:focus { outline: none; border-color: #cba6f7; }

.filter-summary {
  margin-left: auto;
  display: flex; flex-direction: column; align-items: flex-end;
}
.fs-total { font-size: 2rem; font-weight: 700; color: #cba6f7; line-height: 1; }
.fs-label { font-size: .75rem; color: #a6adc8; }

/* ── Secciones ───────────────────────────────────────────────────────────── */
.analytics-section {
  background: #181825;
  border: 1px solid #313244;
  border-radius: 8px;
  padding: 1.25rem;
}

.analytics-section-title {
  font-size: .9rem;
  font-weight: 600;
  color: #cdd6f4;
  margin: 0 0 1rem;
}
.section-subtitle { font-weight: 400; color: #a6adc8; font-size: .8rem; }

.analytics-loading {
  display: flex; align-items: center; gap: .5rem;
  color: #a6adc8; font-size: .85rem; padding: .5rem 0;
}
.analytics-empty { color: #6c7086; font-size: .85rem; padding: .5rem 0; }
.analytics-empty--top { padding: 2rem; text-align: center; }

/* ── Barras horizontales ─────────────────────────────────────────────────── */
.hbar-list { display: flex; flex-direction: column; gap: .5rem; }

.hbar-row {
  display: grid;
  grid-template-columns: 160px 1fr 50px 80px;
  align-items: center;
  gap: .5rem;
}

.hbar-label { font-size: .82rem; color: #cdd6f4; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.hbar-track { background: #1e1e2e; border-radius: 4px; height: 14px; overflow: hidden; }
.hbar-fill { height: 100%; border-radius: 4px; transition: width .3s ease; min-width: 4px; }
.hbar-fill--type    { background: #89b4fa; }
.hbar-fill--ok      { background: #a6e3a1; }
.hbar-fill--warn    { background: #f9e2af; }
.hbar-fill--danger  { background: #f38ba8; }
.hbar-count { font-size: .82rem; color: #cba6f7; font-weight: 600; text-align: right; }
.hbar-users { font-size: .75rem; color: #6c7086; text-align: right; }

/* ── Heatmap por línea ───────────────────────────────────────────────────── */
.code-heatmap {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: .78rem;
  border: 1px solid #313244;
  border-radius: 6px;
  overflow: hidden;
  max-height: 400px;
  overflow-y: auto;
}

.code-line {
  display: flex;
  align-items: center;
  gap: .5rem;
  padding: .2rem .75rem;
  border-bottom: 1px solid #1e1e2e;
  position: relative;
}
.code-line:hover { background: #1e1e2e; }

.line-heat--low  { background: rgba(249, 226, 175, .08); }
.line-heat--mid  { background: rgba(249, 226, 175, .18); }
.line-heat--high { background: rgba(243, 139, 168, .22); }

.code-lineno { color: #45475a; min-width: 2rem; text-align: right; user-select: none; }
.code-text { margin: 0; flex: 1; color: #cdd6f4; white-space: pre; }
.code-badge {
  background: #f38ba8; color: #1e1e2e;
  font-size: .65rem; font-weight: 700;
  padding: .1rem .35rem; border-radius: 10px;
  min-width: 1.4rem; text-align: center;
}

/* ── Tabla historial ─────────────────────────────────────────────────────── */
.analytics-table {
  width: 100%;
  border-collapse: collapse;
  font-size: .82rem;
}
.analytics-table th {
  text-align: left;
  padding: .5rem .75rem;
  color: #a6adc8;
  font-weight: 500;
  border-bottom: 1px solid #313244;
}
.analytics-table td {
  padding: .45rem .75rem;
  color: #cdd6f4;
  border-bottom: 1px solid #1e1e2e;
}
.analytics-table tr:hover td { background: #1e1e2e; }

.error-type-badge {
  background: #313244; color: #f38ba8;
  padding: .15rem .45rem; border-radius: 4px;
  font-size: .75rem; font-family: monospace;
}

/* ── Spinner ─────────────────────────────────────────────────────────────── */
.spinner {
  width: 14px; height: 14px;
  border: 2px solid #313244;
  border-top-color: #cba6f7;
  border-radius: 50%;
  animation: spin .7s linear infinite;
  display: inline-block;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
