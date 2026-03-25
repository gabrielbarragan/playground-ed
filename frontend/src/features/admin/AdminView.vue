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

      <!-- ── Cursos tab ─────────────────────────────────── -->
      <template v-if="activeTab === 'courses'">
        <div class="courses-tab-layout">

          <!-- Formulario -->
          <div class="section course-form-card">
            <h2 class="section-title">Nuevo curso</h2>
            <form class="course-form" @submit.prevent="submitCourse">
              <label class="form-label">
                Nombre
                <input v-model="courseForm.name" class="search-input" style="width:100%" placeholder="Ej: Python Inicial" required />
              </label>
              <label class="form-label">
                Código
                <input v-model="courseForm.code" class="search-input" style="width:100%;text-transform:uppercase" placeholder="Ej: PY2024" required maxlength="20" />
              </label>
              <label class="form-label">
                Descripción
                <input v-model="courseForm.description" class="search-input" style="width:100%" placeholder="Opcional" />
              </label>
              <p v-if="courseError" style="color:#f38ba8;font-size:0.8rem;margin:0">{{ courseError }}</p>
              <button class="btn-primary" type="submit" :disabled="courseSubmitting">
                {{ courseSubmitting ? 'Creando...' : '+ Crear curso' }}
              </button>
            </form>
          </div>

          <!-- Lista -->
          <div class="section" style="flex:1">
            <h2 class="section-title">
              Cursos
              <span class="tab-count">{{ courses.length }}</span>
            </h2>
            <div v-if="loadingCourses" class="table-loading"><span class="spinner" /> Cargando...</div>
            <ul v-else class="course-manage-list">
              <li v-for="course in courses" :key="course.id" class="course-manage-item">
                <div class="course-manage-info">
                  <span class="course-code">{{ course.code }}</span>
                  <span class="course-name">{{ course.name }}</span>
                  <span v-if="course.description" class="course-manage-desc">{{ course.description }}</span>
                </div>
                <div class="course-manage-actions">
                  <span class="status-badge" :class="course.is_active ? 'status--active' : 'status--inactive'">
                    {{ course.is_active ? 'Activo' : 'Inactivo' }}
                  </span>
                  <button
                    class="btn-action"
                    :class="course.is_active ? 'btn-action--deactivate' : 'btn-action--activate'"
                    :disabled="toggleCourseId === course.id"
                    @click="onToggleCourse(course)"
                  >
                    <span v-if="toggleCourseId === course.id" class="spinner spinner--sm" />
                    {{ course.is_active ? 'Desactivar' : 'Activar' }}
                  </button>
                </div>
              </li>
              <li v-if="courses.length === 0" class="table-empty">No hay cursos aún.</li>
            </ul>
          </div>

        </div>
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
                <th class="th-sort" :class="{ 'th-sort--active': sortField === 'name' }" @click="toggleSort('name')">
                  Nombre <span class="sort-icon">{{ sortIcon('name') }}</span>
                </th>
                <th>Email</th>
                <th class="th-sort" :class="{ 'th-sort--active': sortField === 'created_at' }" @click="toggleSort('created_at')">
                  Curso / Registro <span class="sort-icon">{{ sortIcon('created_at') }}</span>
                </th>
                <th class="th-sort" :class="{ 'th-sort--active': sortField === 'points' }" @click="toggleSort('points')">
                  Puntos <span class="sort-icon">{{ sortIcon('points') }}</span>
                </th>
                <th class="th-sort" :class="{ 'th-sort--active': sortField === 'last_login' }" @click="toggleSort('last_login')">
                  Último acceso <span class="sort-icon">{{ sortIcon('last_login') }}</span>
                </th>
                <th>Estado</th>
                <th>Acción</th>
              </tr>
            </thead>
            <tbody>
              <template v-for="user in filteredUsers" :key="user.id">
              <tr :class="{ 'row--inactive': !user.is_active }">
                <td class="cell-name cell-name--link" @click="openProfile(user)">
                  {{ user.first_name }} {{ user.last_name }}
                </td>
                <td class="cell-email">{{ user.email }}</td>
                <td>
                  <div style="display:flex;flex-direction:column;gap:0.15rem">
                    <span v-if="user.course" class="course-badge">{{ user.course.code }}</span>
                    <span v-else class="cell-null">—</span>
                    <span class="cell-date">{{ formatDate(user.created_at) }}</span>
                  </div>
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
                  <div style="display:flex;flex-direction:column;gap:0.3rem;align-items:flex-start">
                    <button
                      class="btn-action"
                      :class="user.is_active ? 'btn-action--deactivate' : 'btn-action--activate'"
                      :disabled="togglingId === user.id"
                      @click="toggleUser(user)"
                    >
                      <span v-if="togglingId === user.id" class="spinner spinner--sm" />
                      {{ user.is_active ? 'Desactivar' : 'Activar' }}
                    </button>
                    <button
                      class="btn-action btn-action--email"
                      @click="startEmailEdit(user)"
                    >
                      ✉ Email
                    </button>
                  </div>
                </td>
              </tr>
              <!-- Inline email edit row -->
              <tr v-if="emailEditUserId === user.id" class="email-edit-row">
                <td colspan="7">
                  <div class="email-edit-box">
                    <span class="email-edit-label">Nuevo email para <strong>{{ user.first_name }} {{ user.last_name }}</strong>:</span>
                    <input
                      v-model="emailEditValue"
                      type="email"
                      class="search-input email-edit-input"
                      placeholder="nuevo@correo.com"
                      @keyup.enter="saveEmail(user)"
                      @keyup.escape="cancelEmailEdit"
                    />
                    <button class="btn-primary btn-sm" :disabled="emailEditSaving" @click="saveEmail(user)">
                      <span v-if="emailEditSaving" class="spinner spinner--sm" />
                      {{ emailEditSaving ? '...' : 'Guardar' }}
                    </button>
                    <button class="btn-action btn-action--deactivate btn-sm" @click="cancelEmailEdit">Cancelar</button>
                    <span v-if="emailEditError" class="email-edit-error">{{ emailEditError }}</span>
                  </div>
                </td>
              </tr>
              </template>
            </tbody>
          </table>
        </div>
      </section>

      </template><!-- end users tab -->

      <!-- ── Evaluaciones tab ───────────────────────────── -->
      <template v-if="activeTab === 'quizzes'">
        <div class="tab-toolbar">
          <span class="tab-toolbar-title">
            Evaluaciones <span class="tab-count">{{ quizzes.length }}</span>
          </span>
          <div class="tab-toolbar-right">
            <label class="toggle-label">
              <input v-model="showInactiveQuizzes" type="checkbox" class="toggle-check" @change="loadQuizzes" />
              <span class="toggle-text">Ver inactivos</span>
            </label>
            <button class="btn-primary" @click="openQuizForm(null)">+ Nuevo quiz</button>
          </div>
        </div>

        <div v-if="loadingQuizzes" class="table-loading"><span class="spinner" /> Cargando...</div>
        <div v-else-if="!quizzes.length" class="table-empty">No hay evaluaciones. Crea la primera.</div>
        <div v-else class="challenges-grid">
          <div
            v-for="q in quizzes" :key="q.id"
            class="challenge-card"
            :class="{ 'challenge-card--inactive': !q.is_active }"
          >
            <div class="cc-header">
              <span v-if="!q.is_active" class="cc-inactive-badge">Inactivo</span>
              <span class="cc-pts">{{ q.points_on_complete + q.points_on_pass }} pts</span>
            </div>
            <h3 class="cc-title">{{ q.title }}</h3>
            <div class="cc-meta">
              <span class="cc-tc">{{ q.question_count }} preguntas · aprobar {{ q.passing_score }}</span>
              <span v-for="course in q.courses" :key="course.id" class="cc-course">{{ course.code }}</span>
            </div>
            <div class="cc-actions">
              <button class="btn-edit" @click="openQuizForm(q)">Editar</button>
              <button class="btn-edit" style="background:#2a1f3d;border-color:#cba6f750;color:#cba6f7" @click="resultsQuiz = q">Resultados</button>
              <button class="btn-deactivate" @click="toggleQuizActive(q)">
                {{ q.is_active ? 'Desactivar' : 'Activar' }}
              </button>
            </div>
          </div>
        </div>

        <!-- Results panel inline -->
        <QuizResultsPanel
          v-if="resultsQuiz"
          :quiz-id="resultsQuiz.id"
          :quiz-title="resultsQuiz.title"
          @close="resultsQuiz = null"
        />
      </template><!-- end quizzes tab -->

      <!-- ── Logros tab ──────────────────────────────────── -->
      <template v-if="activeTab === 'achievements'">
        <div class="tab-toolbar">
          <span class="tab-toolbar-title">
            Logros del Sandbox <span class="tab-count">{{ adminAchievements.length }}</span>
          </span>
          <div class="tab-toolbar-right">
            <label class="toggle-label">
              <input v-model="showInactiveAchievements" type="checkbox" class="toggle-check" @change="loadAchievements" />
              <span class="toggle-text">Ver inactivos</span>
            </label>
            <button class="btn-secondary" style="background:#2a1f3d;border-color:#cba6f750;color:#cba6f7" @click="seedAchievements">
              Cargar logros por defecto
            </button>
          </div>
        </div>

        <div class="courses-tab-layout">
          <!-- Formulario -->
          <div class="section course-form-card">
            <h2 class="section-title">Nuevo logro</h2>
            <form class="course-form" @submit.prevent="submitAchievement">
              <label class="form-label">
                Nombre
                <input v-model="achForm.name" class="search-input" style="width:100%" placeholder="Ej: Maestro del bucle" required />
              </label>
              <label class="form-label">
                Descripción
                <input v-model="achForm.description" class="search-input" style="width:100%" placeholder="Texto al desbloquear" required />
              </label>
              <label class="form-label">
                Icono (emoji)
                <input v-model="achForm.icon" class="search-input" style="width:100%" placeholder="🏆" maxlength="8" />
              </label>
              <label class="form-label">
                Tipo de trigger
                <select v-model="achForm.trigger_type" class="search-input" style="width:100%">
                  <option value="ast_concept">ast_concept</option>
                  <option value="combo">combo</option>
                </select>
              </label>
              <label class="form-label">
                Trigger value
                <input v-model="achForm.trigger_value" class="search-input" style="width:100%" placeholder="loop_while · list_comp · lambda+list_comp" required />
              </label>
              <label class="form-label">
                Puntos bonus
                <input v-model.number="achForm.points_bonus" type="number" min="0" class="search-input" style="width:100%" />
              </label>
              <p v-if="achError" style="color:#f38ba8;font-size:0.8rem;margin:0">{{ achError }}</p>
              <button class="btn-primary" type="submit" :disabled="achSubmitting">
                {{ achSubmitting ? 'Creando...' : '+ Crear logro' }}
              </button>
            </form>
          </div>

          <!-- Lista -->
          <div class="section" style="flex:1">
            <h2 class="section-title">Logros configurados</h2>
            <div v-if="loadingAchievements" class="table-loading"><span class="spinner" /> Cargando...</div>
            <ul v-else class="course-manage-list">
              <li v-for="a in adminAchievements" :key="a.id" class="course-manage-item">
                <div class="course-manage-info">
                  <span style="font-size:1.3rem;flex-shrink:0">{{ a.icon }}</span>
                  <div style="display:flex;flex-direction:column;gap:0.1rem;min-width:0">
                    <span class="course-code">{{ a.name }}</span>
                    <span class="course-name" style="font-size:0.72rem;color:#6c7086">{{ a.trigger_type }} · {{ a.trigger_value }} · +{{ a.points_bonus }} pts</span>
                    <span class="course-manage-desc">{{ a.description }}</span>
                  </div>
                </div>
                <div class="course-manage-actions">
                  <span class="status-badge" :class="a.is_active ? 'status--active' : 'status--inactive'">
                    {{ a.is_active ? 'Activo' : 'Inactivo' }}
                  </span>
                  <button
                    class="btn-action"
                    :class="a.is_active ? 'btn-action--deactivate' : 'btn-action--activate'"
                    @click="toggleAchievement(a)"
                  >
                    {{ a.is_active ? 'Desactivar' : 'Activar' }}
                  </button>
                </div>
              </li>
              <li v-if="!adminAchievements.length" class="table-empty">Sin logros aún. Usa "Cargar logros por defecto".</li>
            </ul>
          </div>
        </div>
      </template><!-- end achievements tab -->

    </main>

    <!-- Modals -->
    <ChallengeFormModal
      v-if="showChallengeForm"
      :challenge="editingChallenge"
      @close="showChallengeForm = false"
      @saved="onChallengeSaved"
    />
    <QuizFormModal
      v-if="showQuizForm"
      :quiz="editingQuiz"
      @close="showQuizForm = false"
      @saved="onQuizSaved"
    />
    <AppFooter />

    <!-- Drawer de perfil de estudiante -->
    <StudentProfileDrawer @go-to-submissions="goToSubmissions" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import AppFooter from '@/components/AppFooter.vue'
import { useAuthStore } from '@/stores/useAuthStore'
import { adminApi, type GlobalStats, type AdminUser, type AdminCourse } from '@/api/adminApi'
import { usersApi } from '@/api/usersApi'
import { challengesApi } from '@/api/challengesApi'
import type { Challenge } from '@/types/challenges'
import ChallengeFormModal from './components/ChallengeFormModal.vue'
import SubmissionsPanel from './components/SubmissionsPanel.vue'
import QuizFormModal from './components/QuizFormModal.vue'
import QuizResultsPanel from './components/QuizResultsPanel.vue'
import { quizzesApi } from '@/api/quizzesApi'
import type { Quiz } from '@/types/quizzes'
import { achievementsApi, type SandboxAchievement } from '@/api/achievementsApi'
import StudentProfileDrawer from './components/StudentProfileDrawer.vue'
import { useStudentProfileStore } from '@/stores/useStudentProfileStore'

const auth = useAuthStore()
const studentProfile = useStudentProfileStore()

function openProfile(user: AdminUser) {
  studentProfile.open(user.id)
}

function goToSubmissions() {
  studentProfile.close()
  activeTab.value = 'submissions'
}

const TABS = [
  { id: 'users', label: 'Usuarios' },
  { id: 'courses', label: 'Cursos' },
  { id: 'challenges', label: 'Retos' },
  { id: 'submissions', label: 'Revisiones' },
  { id: 'quizzes', label: 'Evaluaciones' },
  { id: 'achievements', label: '🏆 Logros' },
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

type SortField = 'name' | 'points' | 'last_login' | 'created_at'
const sortField = ref<SortField>('name')
const sortDir = ref<'asc' | 'desc'>('asc')

function toggleSort(field: SortField) {
  if (sortField.value === field) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortDir.value = field === 'points' || field === 'last_login' ? 'desc' : 'asc'
  }
}

function sortIcon(field: SortField): string {
  if (sortField.value !== field) return '↕'
  return sortDir.value === 'asc' ? '▲' : '▼'
}

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
  const dir = sortDir.value === 'asc' ? 1 : -1
  return [...list].sort((a, b) => {
    switch (sortField.value) {
      case 'name':
        return dir * `${a.last_name} ${a.first_name}`.localeCompare(`${b.last_name} ${b.first_name}`, 'es')
      case 'points':
        return dir * (a.total_points - b.total_points)
      case 'last_login':
        return dir * ((a.last_login ? new Date(a.last_login).getTime() : 0) - (b.last_login ? new Date(b.last_login).getTime() : 0))
      case 'created_at':
        return dir * (new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
      default:
        return 0
    }
  })
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

// ── Courses ─────────────────────────────────────────────────
const courses = ref<AdminCourse[]>([])
const loadingCourses = ref(false)
const toggleCourseId = ref<string | null>(null)
const courseForm = ref({ name: '', code: '', description: '' })
const courseSubmitting = ref(false)
const courseError = ref('')

async function loadCourses() {
  loadingCourses.value = true
  try {
    const res = await adminApi.listCourses()
    courses.value = res.courses
  } finally {
    loadingCourses.value = false
  }
}

async function submitCourse() {
  courseError.value = ''
  courseSubmitting.value = true
  try {
    const created = await adminApi.createCourse({
      name: courseForm.value.name,
      code: courseForm.value.code,
      description: courseForm.value.description,
    })
    courses.value.unshift(created)
    courseForm.value = { name: '', code: '', description: '' }
  } catch (e: any) {
    courseError.value = e?.response?.data?.detail ?? 'Error al crear curso'
  } finally {
    courseSubmitting.value = false
  }
}

async function onToggleCourse(course: AdminCourse) {
  toggleCourseId.value = course.id
  try {
    const updated = await adminApi.toggleCourse(course.id)
    const idx = courses.value.findIndex(c => c.id === course.id)
    if (idx !== -1) courses.value[idx] = updated
  } finally {
    toggleCourseId.value = null
  }
}

// ── Quizzes ─────────────────────────────────────────────────
const quizzes = ref<Quiz[]>([])
const loadingQuizzes = ref(false)
const showInactiveQuizzes = ref(false)
const showQuizForm = ref(false)
const editingQuiz = ref<Quiz | null>(null)
const resultsQuiz = ref<Quiz | null>(null)

async function loadQuizzes() {
  loadingQuizzes.value = true
  try {
    const res = await quizzesApi.adminList(showInactiveQuizzes.value)
    quizzes.value = res.quizzes
  } finally {
    loadingQuizzes.value = false
  }
}

function openQuizForm(q: Quiz | null) {
  editingQuiz.value = q
  showQuizForm.value = true
}

function onQuizSaved(q: Quiz) {
  const idx = quizzes.value.findIndex(x => x.id === q.id)
  if (idx >= 0) quizzes.value[idx] = q
  else quizzes.value.unshift(q)
}

async function toggleQuizActive(q: Quiz) {
  const updated = await quizzesApi.adminToggle(q.id)
  const idx = quizzes.value.findIndex(x => x.id === q.id)
  if (idx >= 0) quizzes.value[idx] = updated
}

// ── Achievements ─────────────────────────────────────────────
const adminAchievements = ref<SandboxAchievement[]>([])
const loadingAchievements = ref(false)
const achForm = ref({ name: '', description: '', icon: '🏆', trigger_type: 'ast_concept', trigger_value: '', points_bonus: 0 })
const achSubmitting = ref(false)
const achError = ref('')
const showInactiveAchievements = ref(false)

async function loadAchievements() {
  loadingAchievements.value = true
  try {
    adminAchievements.value = await achievementsApi.adminList(showInactiveAchievements.value)
  } finally {
    loadingAchievements.value = false
  }
}

async function submitAchievement() {
  achError.value = ''
  achSubmitting.value = true
  try {
    const created = await achievementsApi.adminCreate({ ...achForm.value })
    adminAchievements.value.unshift(created)
    achForm.value = { name: '', description: '', icon: '🏆', trigger_type: 'ast_concept', trigger_value: '', points_bonus: 0 }
  } catch (e: any) {
    achError.value = e?.response?.data?.detail ?? 'Error al crear logro'
  } finally {
    achSubmitting.value = false
  }
}

async function toggleAchievement(a: SandboxAchievement) {
  const updated = await achievementsApi.adminUpdate(a.id, { is_active: !a.is_active })
  const idx = adminAchievements.value.findIndex(x => x.id === a.id)
  if (idx !== -1) adminAchievements.value[idx] = updated
}

// ── Email edit (inline en tabla) ─────────────────────────────
const emailEditUserId = ref<string | null>(null)
const emailEditValue = ref('')
const emailEditSaving = ref(false)
const emailEditError = ref('')

function startEmailEdit(user: AdminUser) {
  emailEditUserId.value = user.id
  emailEditValue.value = user.email
  emailEditError.value = ''
}

function cancelEmailEdit() {
  emailEditUserId.value = null
  emailEditValue.value = ''
  emailEditError.value = ''
}

async function saveEmail(user: AdminUser) {
  emailEditError.value = ''
  if (!emailEditValue.value || emailEditValue.value === user.email) {
    cancelEmailEdit()
    return
  }
  emailEditSaving.value = true
  try {
    const updated = await adminApi.changeUserEmail(user.id, emailEditValue.value)
    const idx = users.value.findIndex(u => u.id === user.id)
    if (idx !== -1) users.value[idx] = updated
    cancelEmailEdit()
  } catch (e: any) {
    emailEditError.value = e?.response?.data?.detail ?? 'Error al actualizar email'
  } finally {
    emailEditSaving.value = false
  }
}

async function seedAchievements() {
  const res = await achievementsApi.adminSeed()
  if (res.created > 0) await loadAchievements()
}

onMounted(async () => {
  const [statsRes] = await Promise.all([adminApi.getStats(), loadUsers(), loadChallenges(), loadCourses(), loadQuizzes(), loadAchievements()])
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

.cell-name--link {
  color: #cba6f7;
  cursor: pointer;
  text-decoration: underline;
  text-decoration-color: transparent;
  text-underline-offset: 2px;
  transition: text-decoration-color 0.15s, color 0.15s;
}
.cell-name--link:hover {
  text-decoration-color: #cba6f7;
}

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

.btn-action--email {
  background: #89b4fa15;
  border-color: #89b4fa40;
  color: #89b4fa;
  font-size: 0.7rem;
  padding: 0.2rem 0.55rem;
}
.btn-action--email:hover { background: #89b4fa25; }


.btn-sm {
  padding: 0.3rem 0.75rem;
  font-size: 0.78rem;
}

.email-edit-row td {
  background: #1e1e2e;
  padding: 0.5rem 1rem;
}

.email-edit-box {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.email-edit-label {
  font-size: 0.78rem;
  color: #a6adc8;
  white-space: nowrap;
}

.email-edit-input {
  width: 220px;
  padding: 0.3rem 0.6rem;
  font-size: 0.82rem;
}

.email-edit-error {
  font-size: 0.75rem;
  color: #f38ba8;
}

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

/* ── Courses tab ─────────────────────────────────────────── */
.courses-tab-layout {
  display: flex;
  gap: 1.5rem;
  align-items: flex-start;
}

.course-form-card {
  min-width: 260px;
  max-width: 300px;
}

.course-form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 0.75rem;
}

.form-label {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.75rem;
  color: #6c7086;
}

.course-manage-list {
  list-style: none;
  padding: 0;
  margin: 0.75rem 0 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.course-manage-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.65rem 0.85rem;
  background: #1e1e2e;
  border-radius: 8px;
  border: 1px solid #313244;
}

.course-manage-info {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  min-width: 0;
}

.course-manage-desc {
  font-size: 0.72rem;
  color: #45475a;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.course-manage-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

/* ── Sortable headers ────────────────────────────────────── */
.th-sort {
  cursor: pointer;
  user-select: none;
  transition: color 0.15s;
}
.th-sort:hover { color: #a6adc8; }
.th-sort--active { color: #cba6f7; }

.sort-icon {
  font-size: 0.6rem;
  opacity: 0.6;
  margin-left: 0.2rem;
  vertical-align: middle;
}
.th-sort--active .sort-icon { opacity: 1; }

/* ── Responsive ──────────────────────────────────────────── */
@media (max-width: 700px) {
  .admin-body { padding: 1rem; }
  .search-input { width: 100%; }
  .table-controls { width: 100%; flex-direction: column; align-items: flex-start; }
  .challenges-grid { grid-template-columns: 1fr; }
  .courses-tab-layout { flex-direction: column; }
  .course-form-card { min-width: unset; max-width: unset; width: 100%; }
}
</style>