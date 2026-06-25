<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-box">
      <h2 class="modal-title">
        Cursos asignados a {{ userName }}
      </h2>

      <div v-if="loading" class="modal-loading">Cargando cursos...</div>
      <div v-else class="course-checks">
        <label
          v-for="course in courses"
          :key="course.id"
          class="course-check-item"
          :class="{ 'course-check-item--selected': selected.has(course.id) }"
        >
          <input
            type="checkbox"
            :checked="selected.has(course.id)"
            @change="toggle(course.id)"
          />
          <div class="course-check-info">
            <span class="course-check-code">{{ course.code }}</span>
            <span class="course-check-name">{{ course.name }}</span>
          </div>
        </label>
        <p v-if="courses.length === 0" class="modal-empty">No hay cursos activos.</p>
      </div>

      <p v-if="error" class="modal-error">{{ error }}</p>

      <div class="modal-actions">
        <button class="btn-cancel" @click="$emit('close')">Cancelar</button>
        <button class="btn-save" :disabled="saving" @click="save">
          {{ saving ? 'Guardando...' : 'Guardar' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { superAdminApi, type SuperAdminCourse } from '@/api/superAdminApi'

const props = defineProps<{
  userId: string
  userName: string
  currentCourseIds: string[]
}>()

const emit = defineEmits<{
  close: []
  saved: [updatedUser: any]
}>()

const courses = ref<SuperAdminCourse[]>([])
const selected = ref(new Set<string>(props.currentCourseIds))
const loading = ref(true)
const saving = ref(false)
const error = ref('')

function toggle(courseId: string) {
  if (selected.value.has(courseId)) {
    selected.value.delete(courseId)
  } else {
    selected.value.add(courseId)
  }
  selected.value = new Set(selected.value)
}

async function save() {
  saving.value = true
  error.value = ''
  try {
    const updated = await superAdminApi.assignCourses(props.userId, [...selected.value])
    emit('saved', updated)
  } catch (e: any) {
    error.value = e?.response?.data?.detail ?? 'Error al asignar cursos'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    const res = await superAdminApi.listCourses()
    courses.value = res.courses.filter(c => c.is_active)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: #00000080;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-box {
  background: #181825;
  border: 1px solid #313244;
  border-radius: 12px;
  padding: 1.5rem;
  min-width: 340px;
  max-width: 440px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.modal-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #cba6f7;
  margin: 0;
}

.modal-loading {
  color: #a6adc8;
  font-size: 0.85rem;
  text-align: center;
  padding: 1rem 0;
}

.course-checks {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  overflow-y: auto;
  max-height: 50vh;
}

.course-check-item {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.5rem 0.75rem;
  background: #1e1e2e;
  border: 1px solid #313244;
  border-radius: 8px;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
}

.course-check-item:hover { border-color: #45475a; }

.course-check-item--selected {
  border-color: #cba6f7;
  background: #2a1f3d;
}

.course-check-item input[type="checkbox"] {
  accent-color: #cba6f7;
  cursor: pointer;
}

.course-check-info {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.course-check-code {
  font-size: 0.7rem;
  font-weight: 700;
  color: #cba6f7;
  font-family: monospace;
}

.course-check-name {
  font-size: 0.82rem;
  color: #cdd6f4;
}

.modal-empty {
  color: #6c7086;
  font-size: 0.85rem;
  text-align: center;
  padding: 1rem 0;
}

.modal-error {
  color: #f38ba8;
  font-size: 0.82rem;
  margin: 0;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.btn-cancel {
  padding: 0.4rem 0.9rem;
  background: #313244;
  border: none;
  border-radius: 6px;
  color: #cdd6f4;
  font-family: inherit;
  font-size: 0.82rem;
  cursor: pointer;
}
.btn-cancel:hover { background: #45475a; }

.btn-save {
  padding: 0.4rem 0.9rem;
  background: #cba6f7;
  border: none;
  border-radius: 6px;
  color: #1e1e2e;
  font-family: inherit;
  font-size: 0.82rem;
  font-weight: 700;
  cursor: pointer;
}
.btn-save:hover:not(:disabled) { opacity: 0.85; }
.btn-save:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
