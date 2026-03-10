<template>
  <div class="admin">
    <!-- Header -->
    <header class="admin-header">
      <div class="admin-header-left">
        <RouterLink to="/" class="back-link">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
            <path d="M19 12H5M12 5l-7 7 7 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          Playground
        </RouterLink>
        <span class="admin-title">Panel Admin</span>
      </div>
      <div class="admin-header-right">
        <span class="admin-chip">{{ auth.user?.email }}</span>
      </div>
    </header>

    <!-- Tabs -->
    <nav class="admin-tabs">
      <button
        v-for="tab in TABS" :key="tab.id"
        class="admin-tab" :class="{ 'admin-tab--active': activeTab === tab.id }"
        @click="activeTab = tab.id"
      >{{ tab.label }}</button>
    </nav>

    <!-- Loading -->
    <div v-if="loadingStats" class="page-loading">
      <span class="big-spinner" />
      <span>Cargando estadísticas...</span>
    </div>

    <main v-else class="admin-body">

      <!-- ── Retos tab ──────────────────────────────────── -->
      <template v-if="activeTab === 'challenges'">
        <div class="tab-toolbar">
          <span class="tab-toolbar-title">
            Retos <span class="tab-count">{{ challenges.length }}</span>
          </span>
          <div class="tab-toolbar-right">
            <label class="toggle-label">
              <input v-model="showInactiveChallenges" type="checkbox" class="toggle-check" @change="loadChallenges" />
              <span class="toggle-text">Ver inactivos</span>
            </label>
            <button class="btn-primary" @click="openChallengeForm(null)">+ Nuevo reto</button>
          </div>
        </div>

        <div v-if="loadingChallenges" class="table-loading"><span class="spinner" /> Cargando...</div>
        <div v-else-if="!challenges.length" class="table-empty">No hay retos. Crea el primero.</div>
        <div v-else class="challenges-grid">
          <div
            v-for="c in challenges" :key="c.id"
            class="challenge-card"
            :class="{ 'challenge-card--inactive': !c.is_active }"
          >
            <div class="cc-header">
              <span class="diff-badge" :class="`diff--${c.difficulty}`">
                {{ c.difficulty === 'easy' ? 'Fácil' : c.difficulty === 'medium' ? 'Media' : 'Difícil' }}
              </span>
              <span class="cc-pts">{{ c.points }} pts</span>
              <span v-if="!c.is_active" class="cc-inactive-badge">Inactivo</span>
              <span v-if="c.requires_review" class="cc-review-badge">Revisión manual</span>
            </div>
            <h3 class="cc-title">{{ c.title }}</h3>
            <div class="cc-meta">
              <span class="cc-tc">{{ c.test_case_count }} test case(s)</span>
              <span v-for="course in c.courses" :key="course.id" class="cc-course">{{ course.code }}</span>
            </div>
            <div class="cc-actions">
              <button class="btn-edit" @click="openChallengeForm(c)">Editar</button>
              <button class="btn-deactivate" @click="toggleChallengeActive(c)">
                {{ c.is_active ? 'Desactivar' : 'Activar' }}
              </button>
            </div>
          </div>
        </div>
      </template>

      <!-- ── Revisiones tab ─────────────────────────────── -->
      <template v-if="activeTab === 'submissions'">
        <SubmissionsPanel />
      </template>

      <!-- ── Usuarios tab ───────────────────────────────── -->
      <template v-if="activeTab === 'users'">

      <!-- Stats row -->
      <section class="stats-row">
        <div class="stat-card stat-card--green">
          <div class="stat-icon-wrap">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <circle cx="9" cy="7" r="4" stroke="currentColor" stroke-width="2"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <path d="M16 3.13a4 4 0 0 1 0 7.75" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ stats?.users.active ?? 0 }}</span>
            <span class="stat-label">Usuarios activos</span>
          </div>
        </div>

        <div class="stat-card stat-card--red">
          <div class="stat-icon-wrap">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
              <line x1="15" y1="9" x2="9" y2="15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <line x1="9" y1="9" x2="15" y2="15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ stats?.users.inactive ?? 0 }}</span>
            <span class="stat-label">Usuarios inactivos</span>
          </div>
        </div>

        <div class="stat-card stat-card--purple">
          <div class="stat-icon-wrap">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <polygon points="5 3 19 12 5 21 5 3"/>
            </svg>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ stats?.executions.last_7_days ?? 0 }}</span>
            <span class="stat-label">Ejecuciones (7d)</span>
          </div>
        </div>

        <div class="stat-card stat-card--blue">
          <div class="stat-icon-wrap">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <path d="M22 12h-4l-3 9L9 3l-3 9H2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ stats?.users.active_last_7_days ?? 0 }}</span>
            <span class="stat-label">Activos esta semana</span>
          </div>
        </div>
      </section>

      <!-- Courses summary -->
      <section class="section">
        <h2 class="section-title">Cursos</h2>
        <div class="courses-grid">
          <div
            v-for="course in stats?.courses"
            :key="course.id"
            class="course-card"
            :class="{ 'course-card--selected': selectedCourseId === course.id }"
            @click="toggleCourseFilter(course.id)"
          >
            <span class="course-code">{{ course.code }}</span>
            <span class="course-name">{{ course.name }}</span>
            <span class="course-users">{{ course.active_users }} alumnos</span>
          </div>
        </div>
      </section>

      <!-- Users table -->
      <section class="section">
        <div class="table-header">
          <h2 class="section-title">
            Usuarios
            <span class="users-count">{{ filteredUsers.length }}</span>
          </h2>
          <div class="table-controls">
            <input
              v-model="searchQuery"
              type="text"
              class="search-input"
              placeholder="Buscar por nombre o email..."
            />
            <label class="toggle-label">
              <input v-model="includeInactive" type="checkbox" class="toggle-check" @change="loadUsers" />
              <span class="toggle-text">Ver inactivos</span>
            </label>
          </div>
        </div>

        <div v-if="loadingUsers" class="table-loading">
          <span class="spinner" /> Cargando usuarios...
        </div>

        <div v-else-if="filteredUsers.length === 0" class="table-empty">
          No se encontraron usuarios.
        </div>

        <div v-else class="table-wrap">
          <table class="users-table">
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Email</th>
                <th>Curso</th>
                <th>Puntos</th>
                <th>Último acceso</th>
                <th>Estado</th>
                <th>Acción</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in filteredUsers" :key="user.id" :class="{ 'row--inactive': !user.is_active }">
                <td class="cell-name">
                  {{ user.first_name }} {{ user.last_name }}
                </td>
                <td class="cell-email">{{ user.email }}</td>
                <td>
                  <span v-if="user.course" class="course-badge">{{ user.course.code }}</span>
                  <span v-else class="cell-null">—</span>
                </td>
                <td class="cell-pts">{{ user.total_points }}</td>
                <td class="cell-date">
                  {{ user.last_login ? formatDate(user.last_login) : '—' }}
                </td>
                <td>
                  <span class="status-badge" :class="user.is_active ? 'status--active' : 'status--inactive'">
                    {{ user.is_active ? 'Activo' : 'Inactivo' }}
                  </span>
                </td>
                <td>
                  <button
                    class="btn-action"
                    :class="user.is_active ? 'btn-action--deactivate' : 'btn-action--activate'"
                    :disabled="togglingId === user.id"
                    @click="toggleUser(user)"
                  >
                    <span v-if="togglingId === user.id" class="spinner spinner--sm" />
                    {{ user.is_active ? 'Desactivar' : 'Activar' }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      </template><!-- end users tab -->

    </main>

    <!-- Modals -->
    <ChallengeFormModal
      v-if="showChallengeForm"
      :challenge="editingChallenge"
      @close="showChallengeForm = false"
      @saved="onChallengeSaved"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/useAuthStore'
import { adminApi, type GlobalStats, type AdminUser } from '@/api/adminApi'
import { challengesApi } from '@/api/challengesApi'
import type { Challenge } from '@/types/challenges'
import ChallengeFormModal from './components/ChallengeFormModal.vue'
import SubmissionsPanel from './components/SubmissionsPanel.vue'

const auth = useAuthStore()

const TABS = [
  { id: 'users', label: 'Usuarios' },
  { id: 'challenges', label: 'Retos' },
  { id: 'submissions', label: 'Revisiones' },
]
const activeTab = ref('users')

// ── Challenges ─────────────────────────────────────────────
const challenges = ref<Challenge[]>([])
const loadingChallenges = ref(false)
const showInactiveChallenges = ref(false)
const showChallengeForm = ref(false)
const editingChallenge = ref<Challenge | null>(null)

async function loadChallenges() {
  loadingChallenges.value = true
  try {
    const res = await challengesApi.adminList(showInactiveChallenges.value)
    challenges.value = res.challenges
  } finally {
    loadingChallenges.value = false
  }
}

function openChallengeForm(c: Challenge | null) {
  editingChallenge.value = c
  showChallengeForm.value = true
}

function onChallengeSaved(c: Challenge) {
  showChallengeForm.value = false
  const idx = challenges.value.findIndex(x => x.id === c.id)
  if (idx >= 0) challenges.value[idx] = c
  else challenges.value.unshift(c)
}

async function toggleChallengeActive(c: Challenge) {
  const updated = await challengesApi.adminUpdate(c.id, { is_active: !c.is_active })
  const idx = challenges.value.findIndex(x => x.id === c.id)
  if (idx >= 0) challenges.value[idx] = updated
}

const stats = ref<GlobalStats | null>(null)
const users = ref<AdminUser[]>([])
const loadingStats = ref(true)
const loadingUsers = ref(false)
const togglingId = ref<string | null>(null)
const searchQuery = ref('')
const includeInactive = ref(false)
const selectedCourseId = ref<string | null>(null)

const filteredUsers = computed(() => {
  let list = users.value
  if (selectedCourseId.value) {
    list = list.filter(u => u.course?.id === selectedCourseId.value)
  }
  const q = searchQuery.value.toLowerCase().trim()
  if (q) {
    list = list.filter(u =>
      `${u.first_name} ${u.last_name}`.toLowerCase().includes(q) ||
      u.email.toLowerCase().includes(q),
    )
  }
  return list
})

async function loadUsers() {
  loadingUsers.value = true
  try {
    const res = await adminApi.listUsers({ include_inactive: includeInactive.value })
    users.value = res.users
  } finally {
    loadingUsers.value = false
  }
}

function toggleCourseFilter(courseId: string) {
  selectedCourseId.value = selectedCourseId.value === courseId ? null : courseId
}

async function toggleUser(user: AdminUser) {
  togglingId.value = user.id
  try {
    const updated = user.is_active
      ? await adminApi.deactivateUser(user.id)
      : await adminApi.activateUser(user.id)
    const idx = users.value.findIndex(u => u.id === updated.id)
    if (idx !== -1) users.value[idx] = updated
    // Refresca stats para que los contadores sean correctos
    stats.value = await adminApi.getStats()
  } finally {
    togglingId.value = null
  }
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('es-AR', {
    day: '2-digit', month: 'short', year: 'numeric',
  })
}

onMounted(async () => {
  const [statsRes] = await Promise.all([adminApi.getStats(), loadUsers(), loadChallenges()])
  stats.value = statsRes
  loadingStats.value = false
})
</script>

<style scoped>
.admin {
  min-height: 100vh;
  background: #1e1e2e;
  color: #cdd6f4;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  display: flex;
  flex-direction: column;
}

/* ── Header ─────────────────────────────────────────────── */
.admin-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.5rem;
  height: 48px;
  background: #181825;
  border-bottom: 1px solid #313244;
  flex-shrink: 0;
}

.admin-header-left {
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

.admin-title {
  font-size: 0.9rem;
  font-weight: 700;
  color: #cdd6f4;
}

.admin-chip {
  font-size: 0.72rem;
  background: #313244;
  color: #f38ba8;
  padding: 0.15rem 0.6rem;
  border-radius: 4px;
}

/* ── Loading ─────────────────────────────────────────────── */
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

/* ── Body ────────────────────────────────────────────────── */
.admin-body {
  flex: 1;
  max-width: 1100px;
  width: 100%;
  margin: 0 auto;
  padding: 2rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
}

/* ── Stats ───────────────────────────────────────────────── */
.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
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
  border-left-width: 3px;
}

.stat-card--green  { border-left-color: #a6e3a1; }
.stat-card--red    { border-left-color: #f38ba8; }
.stat-card--purple { border-left-color: #cba6f7; }
.stat-card--blue   { border-left-color: #89b4fa; }

.stat-icon-wrap {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: #313244;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #a6adc8;
  flex-shrink: 0;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.stat-value {
  font-size: 1.6rem;
  font-weight: 700;
  color: #cdd6f4;
  line-height: 1;
}

.stat-label {
  font-size: 0.72rem;
  color: #6c7086;
}

/* ── Section ─────────────────────────────────────────────── */
.section {
  background: #181825;
  border: 1px solid #313244;
  border-radius: 10px;
  padding: 1.25rem 1.5rem;
}

.section-title {
  font-size: 0.88rem;
  font-weight: 700;
  color: #a6adc8;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.users-count {
  font-size: 0.72rem;
  background: #313244;
  color: #6c7086;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-weight: 400;
}

/* ── Courses grid ────────────────────────────────────────── */
.courses-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 1rem;
}

.course-card {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  padding: 0.75rem 1rem;
  background: #1e1e2e;
  border: 1px solid #313244;
  border-radius: 8px;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
  min-width: 140px;
}

.course-card:hover { border-color: #585b70; }

.course-card--selected {
  border-color: #cba6f7;
  background: #2a1f3d;
}

.course-code {
  font-size: 0.68rem;
  font-weight: 700;
  color: #cba6f7;
  letter-spacing: 0.05em;
}

.course-name {
  font-size: 0.82rem;
  color: #cdd6f4;
  font-weight: 500;
}

.course-users {
  font-size: 0.7rem;
  color: #6c7086;
}

/* ── Table header ────────────────────────────────────────── */
.table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.table-controls {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  flex-wrap: wrap;
}

.search-input {
  padding: 0.45rem 0.85rem;
  background: #1e1e2e;
  border: 1px solid #313244;
  border-radius: 7px;
  color: #cdd6f4;
  font-family: inherit;
  font-size: 0.82rem;
  outline: none;
  width: 220px;
  transition: border-color 0.15s;
}

.search-input::placeholder { color: #45475a; }
.search-input:focus { border-color: #cba6f7; }

.toggle-label {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  cursor: pointer;
  font-size: 0.78rem;
  color: #6c7086;
  user-select: none;
}

.toggle-check { accent-color: #cba6f7; cursor: pointer; }
.toggle-text { transition: color 0.15s; }
.toggle-label:hover .toggle-text { color: #a6adc8; }

/* ── Table ───────────────────────────────────────────────── */
.table-wrap {
  overflow-x: auto;
}

.table-loading,
.table-empty {
  padding: 2rem;
  text-align: center;
  font-size: 0.82rem;
  color: #45475a;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.82rem;
}

.users-table th {
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

.users-table td {
  padding: 0.7rem 0.75rem;
  border-bottom: 1px solid #1e1e2e;
  color: #cdd6f4;
  vertical-align: middle;
}

.users-table tr:last-child td { border-bottom: none; }

.users-table tbody tr:hover td { background: #1e1e2e; }

.row--inactive td { opacity: 0.5; }

.cell-name { font-weight: 500; white-space: nowrap; }

.cell-email {
  color: #6c7086;
  font-size: 0.78rem;
  white-space: nowrap;
}

.cell-pts {
  font-weight: 600;
  color: #a6adc8;
  white-space: nowrap;
}

.cell-date {
  font-size: 0.75rem;
  color: #6c7086;
  white-space: nowrap;
}

.cell-null { color: #45475a; }

.course-badge {
  font-size: 0.68rem;
  background: #313244;
  color: #cba6f7;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  font-weight: 600;
}

.status-badge {
  display: inline-block;
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  white-space: nowrap;
}

.status--active  { background: #a6e3a120; color: #a6e3a1; }
.status--inactive { background: #f38ba820; color: #f38ba8; }

/* ── Actions ─────────────────────────────────────────────── */
.btn-action {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.3rem 0.7rem;
  border-radius: 5px;
  font-size: 0.75rem;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  border: 1px solid transparent;
  transition: background 0.15s, opacity 0.15s;
  white-space: nowrap;
}

.btn-action:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-action--deactivate {
  background: #f38ba815;
  border-color: #f38ba840;
  color: #f38ba8;
}
.btn-action--deactivate:hover:not(:disabled) { background: #f38ba825; }

.btn-action--activate {
  background: #a6e3a115;
  border-color: #a6e3a140;
  color: #a6e3a1;
}
.btn-action--activate:hover:not(:disabled) { background: #a6e3a125; }

/* ── Spinners ────────────────────────────────────────────── */
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

.spinner--sm {
  width: 10px;
  height: 10px;
  border-width: 1.5px;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* ── Tabs ────────────────────────────────────────────────── */
.admin-tabs {
  display: flex;
  gap: 0;
  background: #181825;
  border-bottom: 1px solid #313244;
  padding: 0 1.5rem;
  flex-shrink: 0;
}

.admin-tab {
  padding: 0.65rem 1.1rem;
  font-family: inherit;
  font-size: 0.82rem;
  font-weight: 600;
  color: #6c7086;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: color 0.15s, border-color 0.15s;
  margin-bottom: -1px;
}

.admin-tab:hover { color: #a6adc8; }
.admin-tab--active { color: #cba6f7; border-bottom-color: #cba6f7; }

/* ── Tab toolbar ─────────────────────────────────────────── */
.tab-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
}

.tab-toolbar-title {
  font-size: 0.9rem;
  font-weight: 700;
  color: #a6adc8;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tab-count {
  font-size: 0.72rem;
  background: #313244;
  color: #6c7086;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-weight: 400;
}

.tab-toolbar-right {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  flex-wrap: wrap;
}

.btn-primary {
  padding: 0.45rem 1rem;
  background: #cba6f7;
  color: #1e1e2e;
  border: none;
  border-radius: 7px;
  font-family: inherit;
  font-size: 0.82rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-primary:hover { background: #b794e0; }

/* ── Challenges grid ─────────────────────────────────────── */
.challenges-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}

.challenge-card {
  background: #181825;
  border: 1px solid #313244;
  border-radius: 10px;
  padding: 1rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  transition: border-color 0.15s;
}

.challenge-card:hover { border-color: #45475a; }
.challenge-card--inactive { opacity: 0.55; }

.cc-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.cc-pts {
  font-size: 0.72rem;
  color: #f9e2af;
  font-weight: 700;
  margin-left: auto;
}

.cc-inactive-badge {
  font-size: 0.65rem;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  background: #45475a30;
  color: #6c7086;
  font-weight: 600;
}

.cc-review-badge {
  font-size: 0.65rem;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  background: #89b4fa20;
  color: #89b4fa;
  font-weight: 600;
}

.cc-title {
  font-size: 0.9rem;
  font-weight: 700;
  color: #cdd6f4;
  margin: 0;
}

.cc-meta {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  flex-wrap: wrap;
}

.cc-tc {
  font-size: 0.7rem;
  color: #6c7086;
}

.cc-course {
  font-size: 0.65rem;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  background: #313244;
  color: #cba6f7;
  font-weight: 700;
}

.cc-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.25rem;
}

.btn-edit {
  flex: 1;
  padding: 0.4rem 0.75rem;
  background: #313244;
  border: 1px solid #45475a;
  border-radius: 6px;
  color: #cdd6f4;
  font-family: inherit;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-edit:hover { background: #45475a; }

.btn-deactivate {
  flex: 1;
  padding: 0.4rem 0.75rem;
  background: transparent;
  border: 1px solid #313244;
  border-radius: 6px;
  color: #6c7086;
  font-family: inherit;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
}
.btn-deactivate:hover { border-color: #f38ba8; color: #f38ba8; }

/* ── Difficulty badges ───────────────────────────────────── */
.diff-badge {
  font-size: 0.65rem;
  padding: 0.12rem 0.5rem;
  border-radius: 4px;
  font-weight: 700;
}
.diff--easy   { background: #1e3a1e; color: #a6e3a1; }
.diff--medium { background: #3a2a1e; color: #fab387; }
.diff--hard   { background: #3a1e1e; color: #f38ba8; }

/* ── Responsive ──────────────────────────────────────────── */
@media (max-width: 700px) {
  .admin-body { padding: 1rem; }
  .search-input { width: 100%; }
  .table-controls { width: 100%; flex-direction: column; align-items: flex-start; }
  .challenges-grid { grid-template-columns: 1fr; }
}
</style>