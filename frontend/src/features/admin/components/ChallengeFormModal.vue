<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal" :class="{ 'modal--wide': showTcPanel }">
      <header class="modal-header">
        <h2 class="modal-title">{{ isEdit ? 'Editar reto' : 'Nuevo reto' }}</h2>
        <div class="modal-header-actions">
          <button
            class="btn-tc-toggle"
            :class="{ 'btn-tc-toggle--active': showTcPanel }"
            @click="showTcPanel = !showTcPanel"
          >
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none">
              <path d="M9 11l3 3L22 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Test Cases
            <span class="tc-badge">{{ isEdit ? (challenge?.test_cases.length ?? 0) : pendingTcs.length }}</span>
          </button>
          <button class="btn-close" @click="$emit('close')">✕</button>
        </div>
      </header>

      <div class="modal-body">
        <!-- Columna izquierda: campos del reto -->
        <div class="form-col">
          <div class="form-grid">
            <div class="field field--full">
              <label class="field-label">Título *</label>
              <input v-model="form.title" class="field-input" placeholder="Ej: Suma de dos números" />
            </div>

            <div class="field">
              <label class="field-label">Dificultad *</label>
              <select v-model="form.difficulty" class="field-input">
                <option value="easy">Fácil</option>
                <option value="medium">Media</option>
                <option value="hard">Difícil</option>
              </select>
            </div>

            <div class="field">
              <label class="field-label">Puntos *</label>
              <input v-model.number="form.points" type="number" min="0" class="field-input" />
            </div>

            <div class="field field--full">
              <label class="field-label">Cursos (seleccionar uno o varios)</label>
              <div class="courses-selector">
                <label v-for="c in courses" :key="c.id" class="course-check">
                  <input type="checkbox" :value="c.id" v-model="form.course_ids" />
                  <span class="course-check-label">{{ c.code }} — {{ c.name }}</span>
                </label>
              </div>
            </div>

            <div class="field field--full">
              <label class="field-label">Descripción * <span class="field-hint">(markdown)</span></label>
              <textarea v-model="form.description" class="field-input field-textarea" rows="5"
                placeholder="Describe el problema. Podés usar **negrita**, listas, etc." />
            </div>

            <div class="field">
              <label class="field-label">Input de ejemplo</label>
              <textarea v-model="form.example_input" class="field-input field-code" rows="3"
                placeholder="stdin de ejemplo" />
            </div>

            <div class="field">
              <label class="field-label">Output de ejemplo</label>
              <textarea v-model="form.example_output" class="field-input field-code" rows="3"
                placeholder="stdout esperado" />
            </div>

            <div class="field field--full">
              <label class="field-label">Código inicial <span class="field-hint">(opcional, se precarga en el editor)</span></label>
              <textarea v-model="form.starter_code" class="field-input field-code" rows="4"
                placeholder="def solution():\n    pass" />
            </div>

            <div class="field">
              <label class="field-label">Tags <span class="field-hint">(separados por coma)</span></label>
              <input v-model="tagsInput" class="field-input" placeholder="bucles, listas, strings" />
            </div>

            <div class="field field--center">
              <label class="toggle-row">
                <input type="checkbox" v-model="form.requires_review" class="toggle-check" />
                <span class="toggle-text">Requiere revisión manual del docente</span>
              </label>
            </div>
          </div>
        </div>

        <!-- Columna derecha: Test Cases (panel deslizable) -->
        <div v-if="showTcPanel" class="tc-col">
          <div class="tc-col-inner">
            <div class="tc-col-header">
              <span class="tc-col-title">Test Cases</span>
              <span class="tc-hint">Los ocultos no muestran su contenido al estudiante.</span>
            </div>

            <!-- Lista existente (modo edit) -->
            <template v-if="isEdit">
              <div v-if="challenge && challenge.test_cases.length" class="tc-list">
                <div v-for="(tc, i) in challenge.test_cases" :key="i" class="tc-item">
                  <div class="tc-meta">
                    <span class="tc-index">#{{ i }}</span>
                    <span v-if="tc.is_hidden" class="tc-hidden-badge">Oculto</span>
                    <span v-if="tc.description" class="tc-desc">{{ tc.description }}</span>
                  </div>
                  <div class="tc-io">
                    <div class="tc-io-block">
                      <span class="tc-io-label">Input</span>
                      <pre class="tc-pre">{{ tc.input || '(ninguno)' }}</pre>
                    </div>
                    <div class="tc-io-block">
                      <span class="tc-io-label">Expected output</span>
                      <pre class="tc-pre">{{ tc.expected_output }}</pre>
                    </div>
                  </div>
                  <button class="btn-tc-remove" :disabled="removingTc === i" @click="removeTestCase(i)">
                    <span v-if="removingTc === i" class="spinner spinner--sm" />
                    <span v-else>✕</span>
                  </button>
                </div>
              </div>
              <p v-else class="tc-empty">Sin test cases todavía.</p>
            </template>

            <!-- Lista pendientes (modo create) -->
            <template v-else>
              <div v-if="pendingTcs.length" class="tc-list">
                <div v-for="(tc, i) in pendingTcs" :key="i" class="tc-item">
                  <div class="tc-meta">
                    <span class="tc-index">#{{ i }}</span>
                    <span v-if="(tc as any).is_hidden" class="tc-hidden-badge">Oculto</span>
                    <span v-if="(tc as any).description" class="tc-desc">{{ (tc as any).description }}</span>
                  </div>
                  <div class="tc-io">
                    <div class="tc-io-block">
                      <span class="tc-io-label">Input</span>
                      <pre class="tc-pre">{{ (tc as any).input || '(ninguno)' }}</pre>
                    </div>
                    <div class="tc-io-block">
                      <span class="tc-io-label">Expected output</span>
                      <pre class="tc-pre">{{ (tc as any).expected_output }}</pre>
                    </div>
                  </div>
                  <button class="btn-tc-remove" @click="removePendingTc(i)">✕</button>
                </div>
              </div>
              <p v-else class="tc-empty">Sin test cases todavía.</p>
            </template>

            <!-- Form para agregar -->
            <div class="tc-add">
              <h4 class="tc-add-title">Agregar test case</h4>
              <div class="field">
                <label class="field-label">Input (stdin)</label>
                <textarea v-model="newTc.input" class="field-input field-code" rows="3"
                  placeholder="Dejá vacío si el programa no usa input()" />
              </div>
              <div class="field">
                <label class="field-label">Output esperado *</label>
                <textarea v-model="newTc.expected_output" class="field-input field-code" rows="3"
                  placeholder="Salida exacta que debe producir el código" />
              </div>
              <div class="field">
                <label class="field-label">Descripción</label>
                <input v-model="newTc.description" class="field-input"
                  placeholder="Ej: caso base, número negativo..." />
              </div>
              <label class="toggle-row" style="margin-top: 0.25rem;">
                <input type="checkbox" v-model="newTc.is_hidden" class="toggle-check" />
                <span class="toggle-text">Test case oculto</span>
              </label>
              <div class="tc-add-actions">
                <button class="btn-add-tc" :disabled="!newTc.expected_output.trim() || addingTc" @click="addTestCase">
                  <span v-if="addingTc" class="spinner spinner--sm" />
                  Agregar
                </button>
                <p v-if="tcError" class="tc-error">{{ tcError }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <footer class="modal-footer">
        <button class="btn-cancel" @click="$emit('close')">Cancelar</button>
        <button class="btn-save" :disabled="saving || !form.title || !form.description" @click="save">
          <span v-if="saving" class="spinner spinner--sm" />
          {{ isEdit ? 'Guardar cambios' : 'Crear reto' }}
        </button>
      </footer>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { challengesApi } from '@/api/challengesApi'
import { coursesApi } from '@/api/coursesApi'
import type { Challenge } from '@/types/challenges'
import type { Course } from '@/types/auth'

const props = defineProps<{ challenge?: Challenge | null }>()
const emit = defineEmits<{ (e: 'close'): void; (e: 'saved', c: Challenge): void }>()

const isEdit = computed(() => !!props.challenge)

const courses = ref<Course[]>([])
const saving = ref(false)
const addingTc = ref(false)
const removingTc = ref<number | null>(null)
const tcError = ref('')
const showTcPanel = ref(false)
const challenge = ref<Challenge | null>(props.challenge ?? null)

const form = ref({
  title: '',
  description: '',
  difficulty: 'easy',
  points: 50,
  course_ids: [] as string[],
  starter_code: '',
  example_input: '',
  example_output: '',
  requires_review: false,
})
const tagsInput = ref('')

// Test cases pendientes (modo create)
const pendingTcs = ref<object[]>([])
const newTc = ref({ input: '', expected_output: '', description: '', is_hidden: false })

watch(() => props.challenge, (c) => {
  challenge.value = c ?? null
  if (c) {
    form.value = {
      title: c.title,
      description: c.description,
      difficulty: c.difficulty,
      points: c.points,
      course_ids: c.courses.map(x => x.id),
      starter_code: c.starter_code,
      example_input: c.example_input,
      example_output: c.example_output,
      requires_review: c.requires_review,
    }
    tagsInput.value = c.tags.join(', ')
  }
}, { immediate: true })

async function loadCourses() {
  courses.value = await coursesApi.list()
}
loadCourses()

async function save() {
  saving.value = true
  try {
    const payload = {
      ...form.value,
      tags: tagsInput.value.split(',').map(t => t.trim()).filter(Boolean),
    }
    let saved: Challenge
    if (isEdit.value && challenge.value) {
      saved = await challengesApi.adminUpdate(challenge.value.id, payload)
    } else {
      saved = await challengesApi.adminCreate(payload)
      for (const tc of pendingTcs.value) {
        saved = await challengesApi.addTestCase(saved.id, tc)
      }
    }
    emit('saved', saved)
  } finally {
    saving.value = false
  }
}

async function addTestCase() {
  if (!newTc.value.expected_output.trim()) return
  tcError.value = ''
  const tc = { ...newTc.value }

  if (isEdit.value && challenge.value) {
    addingTc.value = true
    try {
      challenge.value = await challengesApi.addTestCase(challenge.value.id, tc)
      newTc.value = { input: '', expected_output: '', description: '', is_hidden: false }
    } catch (e: any) {
      tcError.value = e?.response?.data?.detail ?? 'Error al agregar el test case'
    } finally {
      addingTc.value = false
    }
  } else {
    pendingTcs.value.push(tc)
    newTc.value = { input: '', expected_output: '', description: '', is_hidden: false }
  }
}

function removePendingTc(index: number) {
  pendingTcs.value.splice(index, 1)
}

async function removeTestCase(index: number) {
  if (!challenge.value) return
  removingTc.value = index
  try {
    challenge.value = await challengesApi.removeTestCase(challenge.value.id, index)
  } finally {
    removingTc.value = null
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.6);
  display: flex; align-items: center; justify-content: center;
  z-index: 200; padding: 1rem;
}

.modal {
  background: #1e1e2e; border: 1px solid #313244; border-radius: 12px;
  width: 100%; max-width: 820px; max-height: 90vh;
  display: flex; flex-direction: column; overflow: hidden;
  transition: max-width 0.25s ease;
}
.modal--wide { max-width: 1200px; }

.modal-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 1rem 1.5rem; border-bottom: 1px solid #313244; flex-shrink: 0;
}
.modal-title { font-size: 1rem; font-weight: 700; color: #cdd6f4; }
.modal-header-actions { display: flex; align-items: center; gap: 0.75rem; }

.btn-tc-toggle {
  display: flex; align-items: center; gap: 0.45rem;
  background: #313244; border: 1px solid #45475a; border-radius: 6px;
  color: #a6adc8; padding: 0.35rem 0.85rem; font-family: inherit;
  font-size: 0.8rem; font-weight: 600; cursor: pointer;
  transition: background 0.15s, border-color 0.15s, color 0.15s;
}
.btn-tc-toggle:hover { background: #45475a; color: #cdd6f4; }
.btn-tc-toggle--active {
  background: #2a1f3d; border-color: #cba6f7; color: #cba6f7;
}

.btn-close {
  background: transparent; border: none; color: #6c7086;
  font-size: 1rem; cursor: pointer; padding: 0.25rem;
}
.btn-close:hover { color: #f38ba8; }

/* ── Body layout ──────────────────────────────────────── */
.modal-body {
  flex: 1; overflow: hidden;
  display: flex; flex-direction: row;
}

/* Columna del formulario */
.form-col {
  flex: 1; overflow-y: auto; padding: 1.5rem;
  min-width: 0;
}
.form-col::-webkit-scrollbar { width: 4px; }
.form-col::-webkit-scrollbar-track { background: transparent; }
.form-col::-webkit-scrollbar-thumb { background: #313244; border-radius: 2px; }

/* Columna de test cases */
.tc-col {
  width: 380px; flex-shrink: 0;
  border-left: 1px solid #313244;
  display: flex; flex-direction: column;
  overflow: hidden;
  background: #181825;
  animation: slideIn 0.2s ease;
}

@keyframes slideIn {
  from { opacity: 0; transform: translateX(12px); }
  to   { opacity: 1; transform: translateX(0); }
}

.tc-col-inner {
  flex: 1; overflow-y: auto;
  display: flex; flex-direction: column;
  gap: 0;
}
.tc-col-inner::-webkit-scrollbar { width: 4px; }
.tc-col-inner::-webkit-scrollbar-track { background: transparent; }
.tc-col-inner::-webkit-scrollbar-thumb { background: #313244; border-radius: 2px; }

.tc-col-header {
  padding: 0.85rem 1rem; border-bottom: 1px solid #313244;
  display: flex; flex-direction: column; gap: 0.2rem; flex-shrink: 0;
  background: #181825; position: sticky; top: 0; z-index: 1;
}
.tc-col-title { font-size: 0.82rem; font-weight: 700; color: #a6adc8; }
.tc-hint { font-size: 0.7rem; color: #6c7086; }

/* ── Form grid ────────────────────────────────────────── */
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.field { display: flex; flex-direction: column; gap: 0.35rem; }
.field--full { grid-column: 1 / -1; }
.field--center { justify-content: center; }
.field-label { font-size: 0.75rem; color: #a6adc8; font-weight: 600; }
.field-hint { font-weight: 400; color: #6c7086; }
.field-input {
  background: #181825; border: 1px solid #313244; border-radius: 6px;
  color: #cdd6f4; padding: 0.5rem 0.75rem; font-family: inherit; font-size: 0.85rem;
  outline: none; transition: border-color 0.15s;
}
.field-input:focus { border-color: #cba6f7; }
.field-textarea { resize: vertical; }
.field-code { font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; resize: vertical; }
select.field-input { cursor: pointer; }

.courses-selector { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.course-check { display: flex; align-items: center; gap: 0.4rem; cursor: pointer; }
.course-check input { accent-color: #cba6f7; }
.course-check-label { font-size: 0.8rem; color: #a6adc8; }

.toggle-row { display: flex; align-items: center; gap: 0.5rem; cursor: pointer; }
.toggle-check { accent-color: #cba6f7; }
.toggle-text { font-size: 0.82rem; color: #a6adc8; }

/* ── TC Badge (header) ────────────────────────────────── */
.tc-badge {
  background: #45475a; color: #cba6f7; font-size: 0.68rem;
  padding: 0.08rem 0.4rem; border-radius: 10px; font-weight: 700;
}
.btn-tc-toggle--active .tc-badge { background: #3b2f5a; }

/* ── TC list ──────────────────────────────────────────── */
.tc-list { display: flex; flex-direction: column; }
.tc-item {
  display: flex; align-items: flex-start; gap: 0.6rem;
  padding: 0.65rem 1rem; border-bottom: 1px solid #313244;
}
.tc-meta { display: flex; align-items: center; gap: 0.35rem; flex-shrink: 0; padding-top: 0.1rem; }
.tc-index { font-size: 0.7rem; color: #6c7086; font-family: monospace; }
.tc-hidden-badge { font-size: 0.62rem; background: #45475a; color: #a6adc8; padding: 0.08rem 0.35rem; border-radius: 4px; }
.tc-desc { font-size: 0.72rem; color: #6c7086; }
.tc-io { display: flex; gap: 0.5rem; flex: 1; flex-wrap: wrap; min-width: 0; }
.tc-io-block { flex: 1; min-width: 80px; }
.tc-io-label { font-size: 0.62rem; color: #6c7086; display: block; margin-bottom: 0.15rem; }
.tc-pre {
  margin: 0; font-family: monospace; font-size: 0.75rem; color: #a6adc8;
  background: #11111b; padding: 0.3rem 0.45rem; border-radius: 4px;
  white-space: pre-wrap; word-break: break-all;
}
.tc-empty { padding: 1rem; font-size: 0.8rem; color: #6c7086; text-align: center; }

.btn-tc-remove {
  background: transparent; border: 1px solid #313244; border-radius: 5px;
  color: #f38ba8; font-size: 0.72rem; cursor: pointer; padding: 0.18rem 0.4rem;
  flex-shrink: 0; transition: background 0.1s;
}
.btn-tc-remove:hover { background: #3a1e1e; }
.btn-tc-remove:disabled { opacity: 0.5; cursor: not-allowed; }

/* ── TC add form ──────────────────────────────────────── */
.tc-add {
  padding: 1rem; border-top: 1px solid #313244;
  display: flex; flex-direction: column; gap: 0.65rem;
  background: #11111b; flex-shrink: 0;
}
.tc-add-title { font-size: 0.75rem; font-weight: 700; color: #6c7086; margin: 0; }
.btn-add-tc {
  background: #313244; border: none; border-radius: 6px; color: #cdd6f4;
  padding: 0.4rem 1rem; font-size: 0.82rem; cursor: pointer; font-family: inherit;
  transition: background 0.15s; display: flex; align-items: center; gap: 0.4rem;
}
.btn-add-tc:hover:not(:disabled) { background: #45475a; }
.btn-add-tc:disabled { opacity: 0.4; cursor: not-allowed; }
.tc-add-actions { display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap; }
.tc-error { font-size: 0.75rem; color: #f38ba8; margin: 0; }

/* ── Footer ───────────────────────────────────────────── */
.modal-footer {
  display: flex; justify-content: flex-end; gap: 0.75rem;
  padding: 1rem 1.5rem; border-top: 1px solid #313244; flex-shrink: 0;
}
.btn-cancel {
  background: transparent; border: 1px solid #313244; border-radius: 6px;
  color: #6c7086; padding: 0.5rem 1.2rem; font-family: inherit; font-size: 0.85rem; cursor: pointer;
}
.btn-cancel:hover { color: #a6adc8; border-color: #45475a; }
.btn-save {
  background: #cba6f7; border: none; border-radius: 6px; color: #1e1e2e;
  padding: 0.5rem 1.4rem; font-family: inherit; font-size: 0.85rem;
  font-weight: 700; cursor: pointer; transition: background 0.15s;
  display: flex; align-items: center; gap: 0.5rem;
}
.btn-save:hover:not(:disabled) { background: #d4b4ff; }
.btn-save:disabled { opacity: 0.5; cursor: not-allowed; }

/* ── Spinners ─────────────────────────────────────────── */
.spinner {
  display: inline-block; width: 14px; height: 14px;
  border: 2px solid #45475a; border-top-color: #cba6f7;
  border-radius: 50%; animation: spin 0.7s linear infinite;
}
.spinner--sm { width: 11px; height: 11px; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>