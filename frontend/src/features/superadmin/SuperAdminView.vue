<template>
  <div class="superadmin-view">
    <header class="sa-header">
      <div class="sa-header__left">
        <span class="sa-header__badge">⚡</span>
        <h1 class="sa-header__title">Superadmin</h1>
      </div>
      <nav class="sa-header__nav">
        <RouterLink to="/" class="btn-link">Playground</RouterLink>
        <RouterLink to="/admin" class="btn-link">Admin</RouterLink>
        <button class="btn-link btn-link--danger" @click="auth.logout(); $router.push('/login')">
          Salir
        </button>
      </nav>
    </header>

    <div class="sa-tabs">
      <button
        class="sa-tab"
        :class="{ 'sa-tab--active': activeTab === 'users' }"
        @click="activeTab = 'users'"
      >
        Usuarios
      </button>
      <button
        class="sa-tab"
        :class="{ 'sa-tab--active': activeTab === 'courses' }"
        @click="activeTab = 'courses'"
      >
        Cursos
      </button>
    </div>

    <!-- TAB USUARIOS -->
    <section v-if="activeTab === 'users'" class="sa-section">
      <div class="sa-toolbar">
        <input
          v-model="userSearch"
          class="sa-input"
          placeholder="Buscar por nombre o email..."
        />
        <label class="sa-toggle-label">
          <input v-model="includeInactive" type="checkbox" @change="loadUsers" />
          Ver inactivos
        </label>
      </div>

      <div v-if="usersLoading" class="sa-loading">Cargando...</div>
      <div v-else-if="usersError" class="sa-error">{{ usersError }}</div>
      <div v-else class="sa-table-wrapper">
        <table class="sa-table">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Email</th>
              <th>Curso</th>
              <th>Estado</th>
              <th>Rol</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="user in filteredUsers"
              :key="user.id"
              :class="{ 'sa-table__row--self': user.id === auth.user?.id }"
            >
              <td>{{ user.first_name }} {{ user.last_name }}</td>
              <td class="sa-table__email">{{ user.email }}</td>
              <td>{{ user.course?.name ?? '—' }}</td>
              <td>
                <span class="sa-badge" :class="user.is_active ? 'sa-badge--green' : 'sa-badge--gray'">
                  {{ user.is_active ? 'Activo' : 'Inactivo' }}
                </span>
              </td>
              <td>
                <select
                  class="sa-select"
                  :value="user.role"
                  :disabled="user.id === auth.user?.id || roleLoading === user.id"
                  @change="onRoleChange(user.id, ($event.target as HTMLSelectElement).value as UserRole)"
                >
                  <option value="student">Estudiante</option>
                  <option value="admin">Admin</option>
                  <option value="superadmin">Superadmin</option>
                </select>
              </td>
            </tr>
            <tr v-if="filteredUsers.length === 0">
              <td colspan="5" class="sa-table__empty">Sin resultados</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- TAB CURSOS -->
    <section v-if="activeTab === 'courses'" class="sa-section">
      <div class="sa-course-layout">
        <!-- Formulario crear curso -->
        <div class="sa-card">
          <h2 class="sa-card__title">Nuevo curso</h2>
          <form class="sa-form" @submit.prevent="submitCourse">
            <label class="sa-label">
              Nombre
              <input v-model="courseForm.name" class="sa-input" placeholder="Ej: Python Avanzado" required />
            </label>
            <label class="sa-label">
              Código
              <input
                v-model="courseForm.code"
                class="sa-input sa-input--upper"
                placeholder="Ej: PY2024"
                required
                maxlength="20"
              />
            </label>
            <label class="sa-label">
              Descripción
              <input v-model="courseForm.description" class="sa-input" placeholder="Opcional" />
            </label>
            <p v-if="courseError" class="sa-error">{{ courseError }}</p>
            <button class="sa-btn sa-btn--primary" type="submit" :disabled="courseSubmitting">
              {{ courseSubmitting ? 'Creando...' : 'Crear curso' }}
            </button>
          </form>
        </div>

        <!-- Lista de cursos -->
        <div class="sa-card sa-card--grow">
          <h2 class="sa-card__title">Cursos existentes</h2>
          <div v-if="coursesLoading" class="sa-loading">Cargando...</div>
          <ul v-else class="sa-course-list">
            <li v-for="course in courses" :key="course.id" class="sa-course-item">
              <div class="sa-course-item__info">
                <span class="sa-course-item__name">{{ course.name }}</span>
                <span class="sa-course-item__code">{{ course.code }}</span>
                <span v-if="course.description" class="sa-course-item__desc">{{ course.description }}</span>
              </div>
              <div class="sa-course-item__actions">
                <span class="sa-badge" :class="course.is_active ? 'sa-badge--green' : 'sa-badge--gray'">
                  {{ course.is_active ? 'Activo' : 'Inactivo' }}
                </span>
                <button
                  class="sa-btn sa-btn--ghost"
                  :disabled="toggleLoading === course.id"
                  @click="onToggleCourse(course.id)"
                >
                  {{ course.is_active ? 'Desactivar' : 'Activar' }}
                </button>
              </div>
            </li>
            <li v-if="courses.length === 0" class="sa-course-item sa-table__empty">
              Sin cursos
            </li>
          </ul>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/useAuthStore'
import { superAdminApi, type SuperAdminUser, type SuperAdminCourse, type UserRole } from '@/api/superAdminApi'

const auth = useAuthStore()

const activeTab = ref<'users' | 'courses'>('users')

// --- Usuarios ---
const users = ref<SuperAdminUser[]>([])
const usersLoading = ref(false)
const usersError = ref('')
const userSearch = ref('')
const includeInactive = ref(false)
const roleLoading = ref<string | null>(null)

const filteredUsers = computed(() => {
  const q = userSearch.value.toLowerCase()
  if (!q) return users.value
  return users.value.filter(
    u =>
      u.first_name.toLowerCase().includes(q) ||
      u.last_name.toLowerCase().includes(q) ||
      u.email.toLowerCase().includes(q),
  )
})

async function loadUsers() {
  usersLoading.value = true
  usersError.value = ''
  try {
    const res = await superAdminApi.listUsers({ include_inactive: includeInactive.value })
    users.value = res.users
  } catch {
    usersError.value = 'Error al cargar usuarios'
  } finally {
    usersLoading.value = false
  }
}

async function onRoleChange(userId: string, role: UserRole) {
  roleLoading.value = userId
  try {
    const updated = await superAdminApi.updateRole(userId, role)
    const idx = users.value.findIndex(u => u.id === userId)
    if (idx !== -1) users.value[idx] = updated
  } catch (e: any) {
    alert(e?.response?.data?.detail ?? 'Error al cambiar rol')
    await loadUsers()
  } finally {
    roleLoading.value = null
  }
}

// --- Cursos ---
const courses = ref<SuperAdminCourse[]>([])
const coursesLoading = ref(false)
const toggleLoading = ref<string | null>(null)

const courseForm = ref({ name: '', code: '', description: '' })
const courseSubmitting = ref(false)
const courseError = ref('')

async function loadCourses() {
  coursesLoading.value = true
  try {
    const res = await superAdminApi.listCourses()
    courses.value = res.courses
  } finally {
    coursesLoading.value = false
  }
}

async function submitCourse() {
  courseError.value = ''
  courseSubmitting.value = true
  try {
    const created = await superAdminApi.createCourse({
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

async function onToggleCourse(courseId: string) {
  toggleLoading.value = courseId
  try {
    const updated = await superAdminApi.toggleCourse(courseId)
    const idx = courses.value.findIndex(c => c.id === courseId)
    if (idx !== -1) courses.value[idx] = updated
  } finally {
    toggleLoading.value = null
  }
}

onMounted(() => {
  loadUsers()
  loadCourses()
})
</script>

<style scoped>
.superadmin-view {
  min-height: 100vh;
  background: #1e1e2e;
  color: #cdd6f4;
  font-family: inherit;
}

/* Header */
.sa-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1.5rem;
  background: #181825;
  border-bottom: 1px solid #313244;
}
.sa-header__left { display: flex; align-items: center; gap: 0.5rem; }
.sa-header__badge { font-size: 1.25rem; }
.sa-header__title { font-size: 1.1rem; font-weight: 600; color: #cba6f7; margin: 0; }
.sa-header__nav { display: flex; align-items: center; gap: 0.75rem; }

.btn-link {
  background: none;
  border: none;
  color: #a6adc8;
  cursor: pointer;
  font-size: 0.875rem;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  text-decoration: none;
  transition: color 0.15s, background 0.15s;
}
.btn-link:hover { color: #cdd6f4; background: #313244; }
.btn-link--danger:hover { color: #f38ba8; background: #2a1a1f; }

/* Tabs */
.sa-tabs {
  display: flex;
  gap: 0.25rem;
  padding: 1rem 1.5rem 0;
  border-bottom: 1px solid #313244;
}
.sa-tab {
  background: none;
  border: none;
  color: #a6adc8;
  cursor: pointer;
  font-family: inherit;
  font-size: 0.9rem;
  padding: 0.5rem 1rem;
  border-bottom: 2px solid transparent;
  transition: color 0.15s, border-color 0.15s;
}
.sa-tab--active { color: #cba6f7; border-bottom-color: #cba6f7; }
.sa-tab:hover:not(.sa-tab--active) { color: #cdd6f4; }

/* Section */
.sa-section { padding: 1.5rem; }

/* Toolbar */
.sa-toolbar {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

/* Input */
.sa-input {
  background: #181825;
  border: 1px solid #313244;
  border-radius: 6px;
  color: #cdd6f4;
  font-size: 0.875rem;
  padding: 0.4rem 0.75rem;
  outline: none;
  width: 100%;
  transition: border-color 0.15s;
}
.sa-input:focus { border-color: #cba6f7; }
.sa-input--upper { text-transform: uppercase; }

/* Toggle label */
.sa-toggle-label {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.875rem;
  color: #a6adc8;
  cursor: pointer;
  white-space: nowrap;
}

/* Table */
.sa-table-wrapper { overflow-x: auto; }
.sa-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}
.sa-table th {
  text-align: left;
  padding: 0.5rem 0.75rem;
  color: #a6adc8;
  font-weight: 500;
  border-bottom: 1px solid #313244;
}
.sa-table td {
  padding: 0.6rem 0.75rem;
  border-bottom: 1px solid #1e1e2e;
}
.sa-table tbody tr:hover { background: #181825; }
.sa-table__row--self { background: #1e1e2e; opacity: 0.6; }
.sa-table__email { color: #a6adc8; font-size: 0.8rem; }
.sa-table__empty { text-align: center; color: #585b70; padding: 1.5rem; }

/* Badge */
.sa-badge {
  display: inline-block;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 500;
  padding: 0.15rem 0.6rem;
}
.sa-badge--green { background: #1a2e1a; color: #a6e3a1; }
.sa-badge--gray  { background: #313244; color: #585b70; }

/* Select */
.sa-select {
  background: #181825;
  border: 1px solid #313244;
  border-radius: 6px;
  color: #cdd6f4;
  font-family: inherit;
  font-size: 0.8rem;
  padding: 0.25rem 0.5rem;
  cursor: pointer;
  outline: none;
}
.sa-select:disabled { opacity: 0.4; cursor: not-allowed; }
.sa-select:focus { border-color: #cba6f7; }

/* Course layout */
.sa-course-layout {
  display: flex;
  gap: 1.5rem;
  align-items: flex-start;
}

/* Card */
.sa-card {
  background: #181825;
  border: 1px solid #313244;
  border-radius: 10px;
  padding: 1.25rem;
  min-width: 280px;
}
.sa-card--grow { flex: 1; }
.sa-card__title {
  font-size: 0.95rem;
  font-weight: 600;
  color: #cba6f7;
  margin: 0 0 1rem;
}

/* Form */
.sa-form { display: flex; flex-direction: column; gap: 0.75rem; }
.sa-label {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.8rem;
  color: #a6adc8;
}

/* Buttons */
.sa-btn {
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-family: inherit;
  font-size: 0.875rem;
  padding: 0.4rem 0.9rem;
  transition: opacity 0.15s, background 0.15s;
}
.sa-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.sa-btn--primary { background: #cba6f7; color: #1e1e2e; font-weight: 600; }
.sa-btn--primary:hover:not(:disabled) { opacity: 0.85; }
.sa-btn--ghost {
  background: #313244;
  color: #cdd6f4;
  font-size: 0.8rem;
  padding: 0.25rem 0.6rem;
}
.sa-btn--ghost:hover:not(:disabled) { background: #45475a; }

/* Course list */
.sa-course-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 0.5rem; }
.sa-course-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.6rem 0.75rem;
  border-radius: 8px;
  background: #1e1e2e;
}
.sa-course-item__info { display: flex; flex-direction: column; gap: 0.1rem; }
.sa-course-item__name { font-size: 0.9rem; color: #cdd6f4; }
.sa-course-item__code { font-size: 0.75rem; color: #cba6f7; font-family: monospace; }
.sa-course-item__desc { font-size: 0.75rem; color: #6c7086; }
.sa-course-item__actions { display: flex; align-items: center; gap: 0.5rem; flex-shrink: 0; }

/* Utils */
.sa-loading { color: #a6adc8; padding: 1rem 0; text-align: center; }
.sa-error { color: #f38ba8; font-size: 0.85rem; }

@media (max-width: 700px) {
  .sa-course-layout { flex-direction: column; }
  .sa-card { min-width: unset; width: 100%; }
}
</style>