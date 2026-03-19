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
      <section class="section">
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
      <section v-if="ranking" class="section">
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
    <AppFooter />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import AppFooter from '@/components/AppFooter.vue'
import { useAuthStore } from '@/stores/useAuthStore'
import { dashboardApi, type HeatmapResponse, type RankingResponse, type ActivityDay } from '@/api/dashboardApi'
import { achievementsApi, type MyAchievementsResponse } from '@/api/achievementsApi'

const auth = useAuthStore()
const loading = ref(true)
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

/* ── Animations ────────────────────────────────────────── */
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Responsive ────────────────────────────────────────── */
@media (max-width: 600px) {
  .dash-body { padding: 1rem; }
  .rank-name { flex: 0 0 120px; }
  .section { padding: 1rem; }
}
</style>