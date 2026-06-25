<template>
  <div class="dashboard">
    <!-- Header -->
    <header class="dash-header">
      <div class="dash-header-left">
        <RouterLink to="/" class="back-link">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
            <path d="M19 12H5M12 5l-7 7 7 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          Playground
        </RouterLink>
        <span class="dash-title">Mi Actividad</span>
      </div>
      <div class="dash-header-right">
        <span class="user-chip">
          {{ auth.user?.first_name }} {{ auth.user?.last_name }}
        </span>
        <span class="course-chip">{{ auth.user?.course.name }}</span>
        <button class="profile-toggle" :class="{ 'profile-toggle--active': showProfile }" @click="showProfile = !showProfile" title="Mi perfil">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
            <circle cx="12" cy="7" r="4" />
          </svg>
        </button>
      </div>
    </header>

    <!-- Loading -->
    <div v-if="loading" class="page-loading">
      <span class="big-spinner" />
      <span>Cargando actividad...</span>
    </div>

    <main v-else class="dash-body">
      <!-- Stats row -->
      <section class="stats-row">
        <div class="stat-card">
          <span class="stat-icon">🔥</span>
          <div class="stat-info">
            <span class="stat-value">{{ activity?.streak_days ?? 0 }}</span>
            <span class="stat-label">Días seguidos</span>
          </div>
        </div>
        <div class="stat-card">
          <span class="stat-icon">▶</span>
          <div class="stat-info">
            <span class="stat-value">{{ activity?.total_executions ?? 0 }}</span>
            <span class="stat-label">Ejecuciones (15d)</span>
          </div>
        </div>
        <div class="stat-card">
          <span class="stat-icon">★</span>
          <div class="stat-info">
            <span class="stat-value">{{ auth.user?.total_points ?? 0 }}</span>
            <span class="stat-label">Puntos totales</span>
          </div>
        </div>
        <div class="stat-card">
          <span class="stat-icon">📝</span>
          <div class="stat-info">
            <span class="stat-value">{{ totalLines }}</span>
            <span class="stat-label">Líneas escritas</span>
          </div>
        </div>
      </section>

      <!-- Heatmap -->
      <section class="section" data-tour="section-activity">
        <div class="section-header">
          <h2 class="section-title">Actividad — últimos 15 días</h2>
          <span class="heatmap-legend">
            <span class="legend-label">Menos</span>
            <span v-for="l in legendLevels" :key="l" class="legend-cell" :style="{ background: levelColor(l) }" />
            <span class="legend-label">Más</span>
          </span>
        </div>

        <div class="heatmap-scroll">
          <div class="heatmap">
            <div
              v-for="day in activity?.days"
              :key="day.date"
              class="heatmap-cell"
              :style="{ background: dayColor(day.executions) }"
              @mouseenter="tooltip = day"
              @mouseleave="tooltip = null"
            >
              <div v-if="tooltip === day" class="heatmap-tooltip">
                <strong>{{ formatDate(day.date) }}</strong>
                <span>{{ day.executions }} ejecuciones</span>
                <span>{{ day.successful_executions }} exitosas</span>
                <span>{{ day.lines_of_code }} líneas</span>
              </div>
            </div>
          </div>

          <div class="heatmap-dates">
            <span
              v-for="day in activity?.days"
              :key="day.date"
              class="heatmap-date-label"
            >
              {{ shortDate(day.date) }}
            </span>
          </div>
        </div>
      </section>

      <!-- Logros recientes -->
      <section v-if="achievements && achievements.earned_count > 0" class="section">
        <div class="section-header">
          <h2 class="section-title">Logros del Sandbox</h2>
          <span class="section-badge">{{ achievements.earned_count }} / {{ achievements.total }}</span>
        </div>
        <div class="ach-recent">
          <div
            v-for="ua in achievements.earned.slice(0, 3)"
            :key="ua.id"
            class="ach-recent-item"
          >
            <span class="ach-recent-icon">{{ ua.achievement.icon }}</span>
            <div class="ach-recent-info">
              <span class="ach-recent-name">{{ ua.achievement.name }}</span>
              <span class="ach-recent-desc">{{ ua.achievement.description }}</span>
            </div>
            <span v-if="ua.achievement.points_bonus > 0" class="ach-recent-pts">
              +{{ ua.achievement.points_bonus }}
            </span>
          </div>
        </div>
        <RouterLink v-if="achievements.earned_count > 3" to="/" class="ach-see-all">
          Ver todos los logros en el Playground →
        </RouterLink>
      </section>

      <!-- Ranking -->
      <section v-if="ranking" class="section" data-tour="section-ranking">
        <div class="section-header">
          <h2 class="section-title">Ranking · {{ ranking.course.name }}</h2>
          <span class="section-badge">{{ ranking.course.code }}</span>
        </div>

        <div class="ranking-list">
          <div
            v-for="entry in ranking.ranking"
            :key="entry.id"
            class="ranking-row"
            :class="{
              'ranking-row--me': entry.id === auth.user?.id,
              'ranking-row--podium': entry.rank <= 3,
            }"
          >
            <span class="rank-pos" :class="`rank-pos--${entry.rank}`">
              {{ entry.rank <= 3 ? podiumIcon(entry.rank) : entry.rank }}
            </span>
            <span class="rank-name">
              {{ entry.first_name }} {{ entry.last_name }}
              <span v-if="entry.id === auth.user?.id" class="rank-you">tú</span>
            </span>
            <div class="rank-bar-wrap">
              <div
                class="rank-bar"
                :style="{ width: barWidth(entry.total_points) + '%' }"
              />
            </div>
            <span class="rank-pts">{{ entry.total_points }} pts</span>
          </div>

          <p v-if="ranking.ranking.length === 0" class="ranking-empty">
            Nadie tiene puntos todavía. ¡Sé el primero!
          </p>
        </div>
      </section>
    </main>

    <!-- Profile sidebar -->
    <aside v-if="showProfile" class="profile-sidebar">
      <div class="ps-header">
        <h2 class="ps-title">Mi Perfil</h2>
        <button class="ps-close" @click="showProfile = false" title="Cerrar">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
            <path d="M18 6L6 18M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div class="ps-body">
        <!-- Info -->
        <div class="ps-section">
          <h3 class="ps-section-title">Información de cuenta</h3>
          <div class="ps-info-grid">
            <div class="ps-info-item">
              <span class="ps-info-label">Nombre</span>
              <span class="ps-info-value">{{ auth.user?.first_name }} {{ auth.user?.last_name }}</span>
            </div>
            <div class="ps-info-item">
              <span class="ps-info-label">Email</span>
              <span class="ps-info-value">{{ auth.user?.email }}</span>
            </div>
            <div class="ps-info-item">
              <span class="ps-info-label">Curso</span>
              <span class="ps-info-value">{{ auth.user?.course?.name ?? '—' }}</span>
            </div>
          </div>
        </div>

        <!-- Tour -->
        <div class="ps-section">
          <h3 class="ps-section-title">Tour de la plataforma</h3>
          <p class="ps-desc">Repetí el tour interactivo para ver las funcionalidades paso a paso.</p>
          <div class="ps-tour-actions">
            <button class="ps-btn" @click="repeatStudentTour">Tour del Playground</button>
            <button v-if="!auth.isAdmin" class="ps-btn" @click="repeatDashboardTour">Tour del Dashboard</button>
            <button v-if="auth.isAdmin" class="ps-btn ps-btn--admin" @click="repeatAdminTour">Tour del Panel Admin</button>
          </div>
        </div>

        <!-- Cambio de curso -->
        <div v-if="!auth.isAdmin" class="ps-section">
          <h3 class="ps-section-title">Mi curso</h3>

          <div v-if="pendingRequest" class="ps-pending">
            <span class="ps-pending-label">Solicitud pendiente</span>
            <span class="ps-pending-detail">
              De <strong>{{ auth.user?.course?.name }}</strong> a <strong>{{ pendingRequest.to_course.name }}</strong>
            </span>
            <span v-if="pendingRequest.reason" class="ps-pending-reason">{{ pendingRequest.reason }}</span>
          </div>

          <div v-else-if="!showCourseForm" class="ps-course-current">
            <p class="ps-desc">
              Estás en <strong>{{ auth.user?.course?.name }}</strong> ({{ auth.user?.course?.code }}).
            </p>
            <button class="ps-btn" @click="showCourseForm = true">Solicitar cambio de curso</button>
          </div>

          <form v-else class="ps-form" @submit.prevent="handleCourseRequest">
            <label class="ps-form-label">
              Curso destino
              <select v-model="selectedCourseId" class="ps-input" required>
                <option value="" disabled>Seleccionar...</option>
                <option v-for="c in availableCourses" :key="c.id" :value="c.id">
                  {{ c.name }} ({{ c.code }})
                </option>
              </select>
            </label>
            <label class="ps-form-label">
              Razón (opcional)
              <input v-model="courseReason" class="ps-input" placeholder="Ej: Cambio de horario" maxlength="500" />
            </label>
            <p v-if="courseError" class="ps-error">{{ courseError }}</p>
            <div class="ps-form-actions">
              <button type="submit" class="ps-btn" :disabled="courseLoading || !selectedCourseId">
                {{ courseLoading ? 'Enviando...' : 'Enviar' }}
              </button>
              <button type="button" class="ps-btn ps-btn--ghost" @click="showCourseForm = false">Cancelar</button>
            </div>
          </form>
        </div>

        <!-- Cambio de email -->
        <div class="ps-section">
          <h3 class="ps-section-title">Cambiar email</h3>

          <form v-if="!emailSent" class="ps-form" @submit.prevent="handleEmailChange">
            <label class="ps-form-label">
              Nuevo correo
              <input v-model="newEmail" type="email" class="ps-input" placeholder="nuevo@correo.com" required />
            </label>
            <p v-if="emailError" class="ps-error">{{ emailError }}</p>
            <button type="submit" class="ps-btn" :disabled="emailLoading">
              {{ emailLoading ? 'Enviando...' : 'Solicitar cambio' }}
            </button>
          </form>

          <div v-else class="ps-success">
            Link de confirmación enviado a <strong>{{ newEmail }}</strong>.
            <button class="ps-link" @click="emailSent = false">Usar otro correo</button>
          </div>
        </div>
      </div>
    </aside>

    <AppFooter />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import AppFooter from '@/components/AppFooter.vue'
import { useAuthStore } from '@/stores/useAuthStore'
import { dashboardApi, type HeatmapResponse, type RankingResponse, type ActivityDay } from '@/api/dashboardApi'
import { achievementsApi, type MyAchievementsResponse } from '@/api/achievementsApi'
import { usersApi } from '@/api/usersApi'
import { coursesApi } from '@/api/coursesApi'
import { courseRequestsApi, type CourseChangeRequest } from '@/api/courseRequestsApi'
import { useTour } from '@/composables/useTour'
import { dashboardTourSteps } from '@/tours/dashboardTour'
import type { Course } from '@/types/auth.d'

const auth = useAuthStore()
const router = useRouter()
const { shouldShowTour, startTour, resetTour } = useTour()
const loading = ref(true)

// ── Profile sidebar ──────────────────────────────────────
const showProfile = ref(false)

// Tour
function repeatStudentTour() {
  resetTour('student')
  router.push({ name: 'playground' })
}
function repeatAdminTour() {
  resetTour('admin')
  router.push({ name: 'admin' })
}
function repeatDashboardTour() {
  resetTour('dashboard')
  showProfile.value = false
  setTimeout(() => startTour(dashboardTourSteps, 'dashboard'), 100)
}

// Cambio de curso
const pendingRequest = ref<CourseChangeRequest | null>(null)
const showCourseForm = ref(false)
const availableCourses = ref<Course[]>([])
const selectedCourseId = ref('')
const courseReason = ref('')
const courseLoading = ref(false)
const courseError = ref('')

async function loadCourseData() {
  try {
    const [courses, pending] = await Promise.all([
      coursesApi.list(),
      courseRequestsApi.getMyPendingRequest(),
    ])
    availableCourses.value = courses.filter(c => c.id !== auth.user?.course?.id)
    pendingRequest.value = pending
  } catch { /* endpoint may not be available */ }
}

async function handleCourseRequest() {
  courseError.value = ''
  if (!selectedCourseId.value) return
  courseLoading.value = true
  try {
    pendingRequest.value = await courseRequestsApi.createRequest(selectedCourseId.value, courseReason.value)
    showCourseForm.value = false
    selectedCourseId.value = ''
    courseReason.value = ''
  } catch (e: any) {
    courseError.value = e?.response?.data?.detail ?? 'Error al enviar la solicitud'
  } finally {
    courseLoading.value = false
  }
}

// Cambio de email
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
    emailError.value = e?.response?.data?.detail ?? 'Error al solicitar el cambio'
  } finally {
    emailLoading.value = false
  }
}
const activity = ref<HeatmapResponse | null>(null)
const ranking = ref<RankingResponse | null>(null)
const achievements = ref<MyAchievementsResponse | null>(null)
const tooltip = ref<ActivityDay | null>(null)
const legendLevels = [0, 1, 2, 3, 4]

const totalLines = computed(() =>
  activity.value?.days.reduce((sum, d) => sum + d.lines_of_code, 0) ?? 0,
)

const maxPoints = computed(() =>
  Math.max(1, ...(ranking.value?.ranking.map(r => r.total_points) ?? [1])),
)

function barWidth(pts: number): number {
  return Math.max(2, (pts / maxPoints.value) * 100)
}

// Color scale: 0 → apagado, 1-2 → bajo, 3-5 → medio, 6-10 → alto, 11+ → máximo
const COLORS = ['#313244', '#4a3b6b', '#7c5cbf', '#a879eb', '#cba6f7']

function dayColor(n: number): string {
  if (n === 0) return COLORS[0]
  if (n <= 2)  return COLORS[1]
  if (n <= 5)  return COLORS[2]
  if (n <= 10) return COLORS[3]
  return COLORS[4]
}

function levelColor(level: number): string {
  return COLORS[level]
}

function formatDate(iso: string): string {
  const [y, m, d] = iso.split('-').map(Number)
  return new Date(y!, m! - 1, d!).toLocaleDateString('es-AR', {
    weekday: 'short', day: '2-digit', month: 'short',
  })
}

function shortDate(iso: string): string {
  const [y, m, d] = iso.split('-').map(Number)
  const date = new Date(y!, m! - 1, d!)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  if (date.getTime() === today.getTime()) return 'Hoy'
  return date.toLocaleDateString('es-AR', { day: '2-digit', month: 'short' })
}

function podiumIcon(rank: number): string {
  return rank === 1 ? '🥇' : rank === 2 ? '🥈' : '🥉'
}

onMounted(async () => {
  try {
    const courseId = auth.user?.course.id
    const [act, rank, ach] = await Promise.all([
      dashboardApi.myActivity(),
      courseId ? dashboardApi.courseRanking(courseId) : Promise.resolve(null),
      achievementsApi.myAchievements().catch(() => null),
      auth.fetchMe(),
    ])
    activity.value = act
    ranking.value = rank
    achievements.value = ach
    if (!auth.isAdmin) loadCourseData()
    if (!auth.isAdmin && shouldShowTour('dashboard')) {
      setTimeout(() => startTour(dashboardTourSteps, 'dashboard'), 400)
    }
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background: #1e1e2e;
  color: #cdd6f4;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  display: flex;
  flex-direction: column;
}

/* ── Header ────────────────────────────────────────────── */
.dash-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.5rem;
  height: 48px;
  background: #181825;
  border-bottom: 1px solid #313244;
  flex-shrink: 0;
  gap: 1rem;
}

.dash-header-left {
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

.dash-title {
  font-size: 0.9rem;
  font-weight: 700;
  color: #cdd6f4;
}

.dash-header-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.user-chip {
  font-size: 0.78rem;
  color: #a6adc8;
}

.course-chip {
  font-size: 0.72rem;
  background: #313244;
  color: #cba6f7;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
}

/* ── Loading ───────────────────────────────────────────── */
.page-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  flex: 1;
  color: #6c7086;
  font-size: 0.85rem;
}

.big-spinner {
  width: 28px;
  height: 28px;
  border: 3px solid #313244;
  border-top-color: #cba6f7;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* ── Body ──────────────────────────────────────────────── */
.dash-body {
  flex: 1;
  max-width: 900px;
  width: 100%;
  margin: 0 auto;
  padding: 2rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* ── Stats ─────────────────────────────────────────────── */
.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 1rem;
}

.stat-card {
  background: #181825;
  border: 1px solid #313244;
  border-radius: 10px;
  padding: 1rem 1.25rem;
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.stat-icon {
  font-size: 1.4rem;
  flex-shrink: 0;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #cdd6f4;
  line-height: 1;
}

.stat-label {
  font-size: 0.72rem;
  color: #6c7086;
}

/* ── Sections ──────────────────────────────────────────── */
.section {
  background: #181825;
  border: 1px solid #313244;
  border-radius: 10px;
  padding: 1.25rem 1.5rem;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.section-title {
  font-size: 0.88rem;
  font-weight: 700;
  color: #a6adc8;
}

.section-badge {
  font-size: 0.72rem;
  background: #313244;
  color: #cba6f7;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
}

/* ── Heatmap ───────────────────────────────────────────── */
.heatmap-legend {
  display: flex;
  align-items: center;
  gap: 4px;
}

.legend-label {
  font-size: 0.68rem;
  color: #45475a;
}

.legend-cell {
  width: 12px;
  height: 12px;
  border-radius: 3px;
}

.heatmap-scroll {
  overflow-x: auto;
}

.heatmap {
  display: flex;
  gap: 5px;
  padding-bottom: 0.5rem;
}

.heatmap-cell {
  width: 36px;
  height: 36px;
  border-radius: 5px;
  flex-shrink: 0;
  position: relative;
  cursor: default;
  transition: filter 0.15s;
}

.heatmap-cell:hover {
  filter: brightness(1.25);
  z-index: 2;
}

.heatmap-tooltip {
  position: absolute;
  bottom: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%);
  background: #11111b;
  border: 1px solid #313244;
  border-radius: 7px;
  padding: 0.5rem 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  white-space: nowrap;
  font-size: 0.72rem;
  color: #a6adc8;
  z-index: 10;
  pointer-events: none;
}

.heatmap-tooltip strong {
  color: #cdd6f4;
  font-size: 0.75rem;
}

.heatmap-dates {
  display: flex;
  gap: 5px;
}

.heatmap-date-label {
  width: 36px;
  flex-shrink: 0;
  font-size: 0.6rem;
  color: #45475a;
  text-align: center;
  overflow: hidden;
  white-space: nowrap;
}

/* ── Ranking ───────────────────────────────────────────── */
.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.ranking-row {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 0.6rem 0.75rem;
  border-radius: 8px;
  background: #1e1e2e;
  transition: background 0.12s;
}

.ranking-row:hover { background: #252535; }

.ranking-row--me {
  background: #2a1f3d;
  border: 1px solid #cba6f730;
}

.rank-pos {
  width: 28px;
  text-align: center;
  font-size: 0.82rem;
  font-weight: 700;
  color: #6c7086;
  flex-shrink: 0;
}

.rank-pos--1, .rank-pos--2, .rank-pos--3 {
  font-size: 1rem;
}

.rank-name {
  font-size: 0.85rem;
  color: #cdd6f4;
  min-width: 0;
  flex: 0 0 180px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.rank-you {
  font-size: 0.65rem;
  background: #cba6f730;
  color: #cba6f7;
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
  font-weight: 600;
}

.rank-bar-wrap {
  flex: 1;
  height: 6px;
  background: #313244;
  border-radius: 3px;
  overflow: hidden;
}

.rank-bar {
  height: 100%;
  background: #cba6f7;
  border-radius: 3px;
  transition: width 0.4s ease;
}

.rank-pts {
  font-size: 0.8rem;
  color: #a6adc8;
  font-weight: 600;
  white-space: nowrap;
  flex-shrink: 0;
  min-width: 60px;
  text-align: right;
}

.ranking-empty {
  font-size: 0.82rem;
  color: #45475a;
  text-align: center;
  padding: 1rem;
}

/* ── Logros recientes ──────────────────────────────────── */
.ach-recent {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.ach-recent-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.75rem;
  background: #1e1e2e;
  border-radius: 8px;
}

.ach-recent-icon {
  font-size: 1.35rem;
  flex-shrink: 0;
}

.ach-recent-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  min-width: 0;
}

.ach-recent-name {
  font-size: 0.82rem;
  font-weight: 700;
  color: #cdd6f4;
}

.ach-recent-desc {
  font-size: 0.72rem;
  color: #6c7086;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.ach-recent-pts {
  font-size: 0.78rem;
  font-weight: 700;
  color: #a6e3a1;
  flex-shrink: 0;
}

.ach-see-all {
  display: block;
  margin-top: 0.75rem;
  font-size: 0.75rem;
  color: #cba6f7;
  text-decoration: none;
  text-align: right;
  transition: opacity 0.15s;
}

.ach-see-all:hover { opacity: 0.8; }

/* ── Profile toggle button ─────────────────────────────── */
.profile-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: #313244;
  border: 1px solid #45475a;
  border-radius: 8px;
  color: #a6adc8;
  cursor: pointer;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
}
.profile-toggle:hover { background: #45475a; color: #cdd6f4; }
.profile-toggle--active { background: #2a1f3d; border-color: #cba6f7; color: #cba6f7; }

/* ── Profile sidebar ──────────────────────────────────── */
.profile-sidebar {
  position: fixed;
  top: 0;
  right: 0;
  height: 100vh;
  width: 340px;
  background: #181825;
  border-left: 1px solid #313244;
  z-index: 50;
  display: flex;
  flex-direction: column;
  box-shadow: -4px 0 24px rgba(0, 0, 0, 0.3);
  animation: slideIn 0.2s ease;
}

@keyframes slideIn {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}

.ps-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.85rem 1.25rem;
  border-bottom: 1px solid #313244;
  flex-shrink: 0;
}

.ps-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #cba6f7;
  margin: 0;
}

.ps-close {
  background: none;
  border: none;
  color: #6c7086;
  cursor: pointer;
  padding: 0.2rem;
  border-radius: 4px;
  display: flex;
  transition: color 0.15s, background 0.15s;
}
.ps-close:hover { color: #cdd6f4; background: #313244; }

.ps-body {
  flex: 1;
  overflow-y: auto;
  padding: 1rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.ps-section {
  padding-bottom: 1.25rem;
  border-bottom: 1px solid #313244;
}
.ps-section:last-child { border-bottom: none; padding-bottom: 0; }

.ps-section-title {
  font-size: 0.82rem;
  font-weight: 700;
  color: #a6adc8;
  margin: 0 0 0.75rem;
}

.ps-desc {
  font-size: 0.78rem;
  color: #6c7086;
  line-height: 1.5;
  margin: 0 0 0.75rem;
}

.ps-info-grid {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.ps-info-item {
  display: flex;
  gap: 0.75rem;
  align-items: baseline;
}

.ps-info-label {
  font-size: 0.72rem;
  color: #585b70;
  min-width: 50px;
}

.ps-info-value {
  font-size: 0.82rem;
  color: #cdd6f4;
}

/* Tour actions */
.ps-tour-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

/* Buttons */
.ps-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.4rem 0.85rem;
  background: #cba6f7;
  color: #1e1e2e;
  border: none;
  border-radius: 6px;
  font-weight: 700;
  font-size: 0.78rem;
  font-family: inherit;
  cursor: pointer;
  transition: background 0.15s;
}
.ps-btn:hover:not(:disabled) { background: #d4b4ff; }
.ps-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.ps-btn--admin { background: #89b4fa; }
.ps-btn--admin:hover:not(:disabled) { background: #a0c4ff; }
.ps-btn--ghost {
  background: #313244;
  color: #cdd6f4;
}
.ps-btn--ghost:hover { background: #45475a; }

/* Course change */
.ps-pending {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0.65rem 0.85rem;
  background: #fab38710;
  border: 1px solid #fab38730;
  border-radius: 8px;
}
.ps-pending-label { font-size: 0.72rem; font-weight: 700; color: #fab387; }
.ps-pending-detail { font-size: 0.78rem; color: #cdd6f4; }
.ps-pending-detail strong { color: #cba6f7; }
.ps-pending-reason { font-size: 0.72rem; color: #a6adc8; font-style: italic; }

.ps-course-current {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

/* Form */
.ps-form {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.ps-form-label {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.72rem;
  color: #6c7086;
}

.ps-input {
  width: 100%;
  padding: 0.4rem 0.65rem;
  background: #1e1e2e;
  border: 1px solid #313244;
  border-radius: 6px;
  color: #cdd6f4;
  font-family: inherit;
  font-size: 0.82rem;
  outline: none;
  transition: border-color 0.15s;
}
.ps-input::placeholder { color: #45475a; }
.ps-input:focus { border-color: #cba6f7; }

.ps-form-actions {
  display: flex;
  gap: 0.5rem;
}

.ps-error {
  font-size: 0.72rem;
  color: #f38ba8;
  margin: 0;
}

.ps-success {
  font-size: 0.78rem;
  color: #a6e3a1;
  padding: 0.5rem 0.75rem;
  background: #a6e3a110;
  border: 1px solid #a6e3a130;
  border-radius: 6px;
}
.ps-success strong { color: #cdd6f4; }

.ps-link {
  display: block;
  margin-top: 0.5rem;
  font-size: 0.72rem;
  color: #cba6f7;
  background: none;
  border: none;
  cursor: pointer;
  font-family: inherit;
  text-decoration: underline;
  padding: 0;
}

/* ── Animations ────────────────────────────────────────── */
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Responsive ────────────────────────────────────────── */
@media (max-width: 600px) {
  .dash-body { padding: 1rem; }
  .rank-name { flex: 0 0 120px; }
  .section { padding: 1rem; }
  .profile-sidebar { width: 100%; }
}
</style>