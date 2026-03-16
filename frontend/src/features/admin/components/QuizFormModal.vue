<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <!-- Header -->
      <header class="modal-header">
        <h2 class="modal-title">{{ quiz ? 'Editar Quiz' : 'Nuevo Quiz' }}</h2>
        <button class="modal-close" @click="$emit('close')">✕</button>
      </header>

      <!-- Two-panel layout: left = quiz fields, right = questions -->
      <div class="modal-body">

        <!-- LEFT: Quiz fields -->
        <div class="panel-left">
          <h3 class="panel-title">Configuración del Quiz</h3>

          <div class="field-group">
            <label class="field-label">Título *</label>
            <input v-model="form.title" class="field-input" placeholder="Ej: Evaluación Unidad 1" maxlength="200" />
          </div>

          <div class="field-group">
            <label class="field-label">Descripción</label>
            <textarea v-model="form.description" class="field-input field-textarea" rows="2" placeholder="Descripción opcional..." />
          </div>

          <div class="field-group">
            <label class="field-label">Cursos</label>
            <div class="courses-check-list">
              <label
                v-for="course in availableCourses"
                :key="course.id"
                class="course-check-label"
                :class="{ 'course-check-label--active': form.course_ids.includes(course.id) }"
              >
                <input
                  type="checkbox"
                  :value="course.id"
                  v-model="form.course_ids"
                  class="course-check-input"
                />
                <span class="course-code">{{ course.code }}</span>
                <span class="course-name">{{ course.name }}</span>
              </label>
            </div>
          </div>

          <div class="field-row">
            <div class="field-group">
              <label class="field-label">Correctas para aprobar *</label>
              <input v-model.number="form.passing_score" type="number" min="1" class="field-input field-number" />
            </div>
            <div class="field-group">
              <label class="field-label">Pts por entregar</label>
              <input v-model.number="form.points_on_complete" type="number" min="0" class="field-input field-number" />
            </div>
            <div class="field-group">
              <label class="field-label">Pts extra por aprobar</label>
              <input v-model.number="form.points_on_pass" type="number" min="0" class="field-input field-number" />
            </div>
          </div>

          <label class="toggle-row">
            <input v-model="form.show_correct_answers" type="checkbox" class="toggle-check" />
            <span class="toggle-text">Mostrar respuestas correctas al terminar</span>
          </label>

          <div v-if="formError" class="form-error">{{ formError }}</div>

          <button class="btn-save" :disabled="saving" @click="handleSave">
            <span v-if="saving" class="spinner spinner--sm" />
            {{ quiz ? 'Guardar cambios' : 'Crear Quiz' }}
          </button>
        </div>

        <!-- RIGHT: Questions panel (only when quiz is saved) -->
        <div class="panel-right">
          <div v-if="!savedQuiz" class="panel-right-placeholder">
            Guardá el quiz primero para agregar preguntas.
          </div>

          <template v-else>
            <div class="panel-title-row">
              <h3 class="panel-title">Preguntas <span class="q-count">{{ savedQuiz.questions.length }}</span></h3>
              <button class="btn-add-q" @click="openQuestionForm(null)">+ Agregar</button>
            </div>

            <div v-if="!savedQuiz.questions.length" class="questions-empty">
              Sin preguntas aún.
            </div>

            <div class="questions-list">
              <div
                v-for="(q, i) in savedQuiz.questions"
                :key="i"
                class="question-item"
              >
                <div class="qi-left">
                  <span class="qi-num">{{ i + 1 }}</span>
                  <span class="qi-text">{{ q.text.slice(0, 80) }}{{ q.text.length > 80 ? '…' : '' }}</span>
                </div>
                <div class="qi-actions">
                  <button class="btn-qi-edit" @click="openQuestionForm(i)">Editar</button>
                  <button class="btn-qi-del" @click="handleRemoveQuestion(i)">✕</button>
                </div>
              </div>
            </div>

            <!-- Question form -->
            <div v-if="showQForm" class="q-form">
              <h4 class="q-form-title">{{ editingQIndex !== null ? `Editando pregunta ${editingQIndex + 1}` : 'Nueva pregunta' }}</h4>

              <div class="field-group">
                <label class="field-label">Enunciado *</label>
                <textarea v-model="qForm.text" class="field-input field-textarea" rows="3" placeholder="Texto de la pregunta..." />
              </div>

              <div class="field-group">
                <label class="field-label">Bloque de código (opcional)</label>
                <textarea v-model="qForm.code_block" class="field-input field-textarea field-code" rows="4" placeholder="Código Python aquí..." spellcheck="false" />
              </div>

              <div class="field-row field-row--tight">
                <div class="field-group">
                  <label class="field-label">Lenguaje</label>
                  <select v-model="qForm.code_language" class="field-input">
                    <option value="python">Python</option>
                    <option value="javascript">JavaScript</option>
                    <option value="bash">Bash</option>
                    <option value="text">Texto</option>
                  </select>
                </div>
              </div>

              <!-- Options -->
              <div class="field-group">
                <label class="field-label">Opciones (2–6) · seleccioná la correcta</label>
                <div class="options-editor">
                  <div v-for="(opt, j) in qForm.options" :key="j" class="option-row">
                    <input
                      type="radio"
                      :name="'correct-opt'"
                      :value="j"
                      v-model="qForm.correct_option_index"
                      class="option-radio"
                      title="Marcar como correcta"
                    />
                    <input
                      v-model="qForm.options[j].text"
                      class="field-input option-input"
                      :placeholder="`Opción ${j + 1}`"
                      maxlength="500"
                    />
                    <button
                      v-if="qForm.options.length > 2"
                      class="btn-del-opt"
                      @click="removeOption(j)"
                    >✕</button>
                  </div>
                  <button
                    v-if="qForm.options.length < 6"
                    class="btn-add-opt"
                    @click="addOption"
                  >+ Opción</button>
                </div>
              </div>

              <div class="field-group">
                <label class="field-label">Explicación (se muestra al estudiante si show_correct_answers=true)</label>
                <textarea v-model="qForm.explanation" class="field-input field-textarea" rows="2" placeholder="Explicación opcional..." />
              </div>

              <div v-if="qFormError" class="form-error">{{ qFormError }}</div>

              <div class="q-form-actions">
                <button class="btn-cancel-q" @click="showQForm = false">Cancelar</button>
                <button class="btn-save-q" :disabled="savingQ" @click="handleSaveQuestion">
                  <span v-if="savingQ" class="spinner spinner--sm" />
                  {{ editingQIndex !== null ? 'Guardar pregunta' : 'Agregar pregunta' }}
                </button>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { quizzesApi } from '@/api/quizzesApi'
import { adminApi } from '@/api/adminApi'
import type { Quiz } from '@/types/quizzes'

const props = defineProps<{ quiz: Quiz | null }>()
const emit = defineEmits<{
  close: []
  saved: [quiz: Quiz]
}>()

interface OptionForm { text: string }
interface QForm {
  text: string
  code_block: string
  code_language: string
  options: OptionForm[]
  correct_option_index: number
  explanation: string
}

// ── Quiz form ─────────────────────────────────────────────
const form = reactive({
  title: props.quiz?.title ?? '',
  description: props.quiz?.description ?? '',
  course_ids: props.quiz?.courses.map(c => c.id) ?? [],
  passing_score: props.quiz?.passing_score ?? 1,
  points_on_complete: props.quiz?.points_on_complete ?? 0,
  points_on_pass: props.quiz?.points_on_pass ?? 0,
  show_correct_answers: props.quiz?.show_correct_answers ?? true,
})

const savedQuiz = ref<Quiz | null>(props.quiz)
const availableCourses = ref<{ id: string; name: string; code: string }[]>([])
const saving = ref(false)
const formError = ref('')

async function handleSave() {
  formError.value = ''
  if (!form.title.trim()) { formError.value = 'El título es requerido.'; return }
  if (form.passing_score < 1) { formError.value = 'Correctas para aprobar debe ser ≥ 1.'; return }

  saving.value = true
  try {
    let result: Quiz
    if (savedQuiz.value) {
      result = await quizzesApi.adminUpdate(savedQuiz.value.id, {
        title: form.title,
        description: form.description,
        course_ids: form.course_ids,
        passing_score: form.passing_score,
        points_on_complete: form.points_on_complete,
        points_on_pass: form.points_on_pass,
        show_correct_answers: form.show_correct_answers,
      })
    } else {
      result = await quizzesApi.adminCreate({
        title: form.title,
        description: form.description,
        course_ids: form.course_ids,
        passing_score: form.passing_score,
        points_on_complete: form.points_on_complete,
        points_on_pass: form.points_on_pass,
        show_correct_answers: form.show_correct_answers,
      })
    }
    savedQuiz.value = result
    emit('saved', result)
  } catch (e: unknown) {
    const detail = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    formError.value = detail ?? 'Error al guardar el quiz.'
  } finally {
    saving.value = false
  }
}

// ── Question form ─────────────────────────────────────────
const showQForm = ref(false)
const editingQIndex = ref<number | null>(null)
const savingQ = ref(false)
const qFormError = ref('')

const qForm = reactive<QForm>({
  text: '',
  code_block: '',
  code_language: 'python',
  options: [{ text: '' }, { text: '' }],
  correct_option_index: 0,
  explanation: '',
})

function resetQForm() {
  qForm.text = ''
  qForm.code_block = ''
  qForm.code_language = 'python'
  qForm.options = [{ text: '' }, { text: '' }]
  qForm.correct_option_index = 0
  qForm.explanation = ''
  qFormError.value = ''
}

function openQuestionForm(index: number | null) {
  if (index !== null && savedQuiz.value) {
    const q = savedQuiz.value.questions[index]
    qForm.text = q.text
    qForm.code_block = q.code_block ?? ''
    qForm.code_language = q.code_language ?? 'python'
    qForm.options = q.options.map(o => ({ text: o.text }))
    qForm.correct_option_index = (q as unknown as { correct_option_index: number }).correct_option_index ?? 0
    qForm.explanation = (q as unknown as { explanation?: string }).explanation ?? ''
  } else {
    resetQForm()
  }
  editingQIndex.value = index
  showQForm.value = true
}

function addOption() {
  if (qForm.options.length < 6) qForm.options.push({ text: '' })
}

function removeOption(j: number) {
  qForm.options.splice(j, 1)
  if (qForm.correct_option_index >= qForm.options.length) {
    qForm.correct_option_index = qForm.options.length - 1
  }
}

async function handleSaveQuestion() {
  qFormError.value = ''
  if (!qForm.text.trim()) { qFormError.value = 'El enunciado es requerido.'; return }
  if (qForm.options.some(o => !o.text.trim())) { qFormError.value = 'Todas las opciones deben tener texto.'; return }
  if (qForm.correct_option_index >= qForm.options.length) { qFormError.value = 'Seleccioná una opción correcta.'; return }
  if (!savedQuiz.value) return

  savingQ.value = true
  try {
    const payload = {
      text: qForm.text,
      code_block: qForm.code_block,
      code_language: qForm.code_language,
      options: qForm.options,
      correct_option_index: qForm.correct_option_index,
      explanation: qForm.explanation,
    }

    let result: Quiz
    if (editingQIndex.value !== null) {
      result = await quizzesApi.updateQuestion(savedQuiz.value.id, editingQIndex.value, payload)
    } else {
      result = await quizzesApi.addQuestion(savedQuiz.value.id, payload)
    }
    savedQuiz.value = result
    emit('saved', result)
    showQForm.value = false
    resetQForm()
  } catch (e: unknown) {
    const detail = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    qFormError.value = detail ?? 'Error al guardar la pregunta.'
  } finally {
    savingQ.value = false
  }
}

async function handleRemoveQuestion(index: number) {
  if (!savedQuiz.value) return
  if (!confirm(`¿Eliminar la pregunta ${index + 1}?`)) return
  const result = await quizzesApi.removeQuestion(savedQuiz.value.id, index)
  savedQuiz.value = result
  emit('saved', result)
  if (showQForm.value && editingQIndex.value === index) showQForm.value = false
}

onMounted(async () => {
  const stats = await adminApi.getStats()
  availableCourses.value = stats.courses.map((c: { id: string; name: string; code: string }) => ({
    id: c.id,
    name: c.name,
    code: c.code,
  }))
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: #00000088;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
  padding: 1rem;
}

.modal {
  background: #1e1e2e;
  border: 1px solid #313244;
  border-radius: 12px;
  width: 100%;
  max-width: 1000px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Header */
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #313244;
  flex-shrink: 0;
}

.modal-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #cdd6f4;
  margin: 0;
}

.modal-close {
  background: transparent;
  border: none;
  color: #6c7086;
  font-size: 0.9rem;
  cursor: pointer;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  transition: color 0.15s;
}
.modal-close:hover { color: #f38ba8; }

/* Body — two panels */
.modal-body {
  display: grid;
  grid-template-columns: 360px 1fr;
  flex: 1;
  overflow: hidden;
}

/* Left panel */
.panel-left {
  padding: 1.25rem 1.5rem;
  border-right: 1px solid #313244;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.panel-title {
  font-size: 0.82rem;
  font-weight: 700;
  color: #a6adc8;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.field-label {
  font-size: 0.72rem;
  color: #6c7086;
  font-weight: 600;
}

.field-input {
  padding: 0.5rem 0.75rem;
  background: #181825;
  border: 1px solid #313244;
  border-radius: 7px;
  color: #cdd6f4;
  font-family: inherit;
  font-size: 0.82rem;
  outline: none;
  transition: border-color 0.15s;
  width: 100%;
  box-sizing: border-box;
}
.field-input:focus { border-color: #cba6f7; }
.field-textarea { resize: vertical; }
.field-number { width: 90px; }
.field-code { font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; }

.field-row {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  align-items: flex-end;
}
.field-row--tight { gap: 0.5rem; }

.courses-check-list {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  max-height: 120px;
  overflow-y: auto;
}

.course-check-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.45rem 0.75rem;
  background: #181825;
  border: 1px solid #313244;
  border-radius: 6px;
  cursor: pointer;
  transition: border-color 0.15s;
  font-size: 0.8rem;
}
.course-check-label--active { border-color: #cba6f7; background: #2a1f3d; }
.course-check-input { accent-color: #cba6f7; }
.course-code { font-weight: 700; color: #cba6f7; font-size: 0.72rem; }
.course-name { color: #a6adc8; }

.toggle-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.8rem;
  color: #a6adc8;
  user-select: none;
}
.toggle-check { accent-color: #cba6f7; cursor: pointer; }
.toggle-text { transition: color 0.15s; }

.form-error {
  font-size: 0.78rem;
  color: #f38ba8;
  background: #f38ba810;
  border: 1px solid #f38ba830;
  border-radius: 6px;
  padding: 0.5rem 0.75rem;
}

.btn-save {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.55rem 1.25rem;
  background: #cba6f7;
  color: #1e1e2e;
  border: none;
  border-radius: 8px;
  font-family: inherit;
  font-size: 0.85rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.15s;
  align-self: flex-start;
}
.btn-save:hover:not(:disabled) { background: #b794e0; }
.btn-save:disabled { opacity: 0.5; cursor: not-allowed; }

/* Right panel */
.panel-right {
  padding: 1.25rem 1.5rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.panel-right-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  font-size: 0.82rem;
  color: #45475a;
  text-align: center;
  padding: 2rem;
}

.panel-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.q-count {
  font-size: 0.72rem;
  background: #313244;
  color: #6c7086;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-weight: 400;
}

.btn-add-q {
  padding: 0.35rem 0.85rem;
  background: #313244;
  border: 1px solid #45475a;
  border-radius: 6px;
  color: #cba6f7;
  font-family: inherit;
  font-size: 0.78rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-add-q:hover { background: #45475a; }

.questions-empty {
  font-size: 0.82rem;
  color: #45475a;
  padding: 1rem 0;
}

.questions-list {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.question-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.6rem 0.85rem;
  background: #181825;
  border: 1px solid #313244;
  border-radius: 7px;
}

.qi-left {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  overflow: hidden;
}

.qi-num {
  font-size: 0.68rem;
  font-weight: 700;
  color: #cba6f7;
  background: #2a1f3d;
  padding: 0.1rem 0.4rem;
  border-radius: 3px;
  flex-shrink: 0;
}

.qi-text {
  font-size: 0.8rem;
  color: #a6adc8;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.qi-actions {
  display: flex;
  gap: 0.35rem;
  flex-shrink: 0;
}

.btn-qi-edit {
  padding: 0.25rem 0.6rem;
  background: #313244;
  border: 1px solid #45475a;
  border-radius: 5px;
  color: #cdd6f4;
  font-family: inherit;
  font-size: 0.72rem;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-qi-edit:hover { background: #45475a; }

.btn-qi-del {
  padding: 0.25rem 0.5rem;
  background: transparent;
  border: 1px solid #313244;
  border-radius: 5px;
  color: #6c7086;
  font-family: inherit;
  font-size: 0.72rem;
  cursor: pointer;
  transition: border-color 0.15s, color 0.15s;
}
.btn-qi-del:hover { border-color: #f38ba8; color: #f38ba8; }

/* Question form */
.q-form {
  background: #181825;
  border: 1px solid #313244;
  border-radius: 10px;
  padding: 1rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.q-form-title {
  font-size: 0.78rem;
  font-weight: 700;
  color: #cba6f7;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.options-editor {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.option-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.option-radio { accent-color: #cba6f7; cursor: pointer; flex-shrink: 0; }

.option-input { flex: 1; }

.btn-del-opt {
  padding: 0.25rem 0.5rem;
  background: transparent;
  border: 1px solid #313244;
  border-radius: 5px;
  color: #6c7086;
  font-family: inherit;
  font-size: 0.72rem;
  cursor: pointer;
  transition: border-color 0.15s, color 0.15s;
  flex-shrink: 0;
}
.btn-del-opt:hover { border-color: #f38ba8; color: #f38ba8; }

.btn-add-opt {
  align-self: flex-start;
  padding: 0.3rem 0.75rem;
  background: transparent;
  border: 1px dashed #45475a;
  border-radius: 6px;
  color: #6c7086;
  font-family: inherit;
  font-size: 0.75rem;
  cursor: pointer;
  transition: border-color 0.15s, color 0.15s;
}
.btn-add-opt:hover { border-color: #cba6f7; color: #cba6f7; }

.q-form-actions {
  display: flex;
  gap: 0.6rem;
  justify-content: flex-end;
}

.btn-cancel-q {
  padding: 0.4rem 0.9rem;
  background: transparent;
  border: 1px solid #313244;
  border-radius: 7px;
  color: #6c7086;
  font-family: inherit;
  font-size: 0.8rem;
  cursor: pointer;
  transition: border-color 0.15s, color 0.15s;
}
.btn-cancel-q:hover { border-color: #585b70; color: #a6adc8; }

.btn-save-q {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.4rem 1rem;
  background: #cba6f7;
  color: #1e1e2e;
  border: none;
  border-radius: 7px;
  font-family: inherit;
  font-size: 0.8rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-save-q:hover:not(:disabled) { background: #b794e0; }
.btn-save-q:disabled { opacity: 0.5; cursor: not-allowed; }

/* Spinner */
.spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid #31324480;
  border-top-color: #1e1e2e;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
.spinner--sm { width: 10px; height: 10px; border-width: 1.5px; }

@keyframes spin { to { transform: rotate(360deg); } }

/* Responsive */
@media (max-width: 750px) {
  .modal-body { grid-template-columns: 1fr; }
  .panel-left { border-right: none; border-bottom: 1px solid #313244; }
}
</style>