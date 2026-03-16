<template>
  <div class="runner-overlay" @click.self="$emit('close')">
    <div class="runner-modal">
      <!-- Header -->
      <header class="runner-header">
        <div class="runner-header-left">
          <h2 class="runner-title">{{ quiz.title }}</h2>
          <span class="runner-meta">{{ quiz.question_count }} preguntas · aprobar con {{ quiz.passing_score }} correctas</span>
        </div>
        <button class="runner-close" @click="$emit('close')">✕</button>
      </header>

      <!-- Progress bar -->
      <div class="runner-progress-bar">
        <div
          class="runner-progress-fill"
          :style="{ width: `${progressPercent}%` }"
        />
      </div>

      <!-- Questions -->
      <div class="runner-body">
        <div
          v-for="(q, i) in quiz.questions"
          :key="i"
          class="question-block"
        >
          <div class="question-number">Pregunta {{ i + 1 }}</div>
          <div class="question-text">{{ q.text }}</div>
          <QuizCodeBlock v-if="q.code_block" :code="q.code_block" />
          <div class="options-list">
            <label
              v-for="(opt, j) in q.options"
              :key="j"
              class="option-label"
              :class="{ 'option-label--selected': answers[i] === j }"
            >
              <input
                type="radio"
                :name="`q${i}`"
                :value="j"
                v-model="answers[i]"
                class="option-radio"
              />
              <span class="option-text">{{ opt.text }}</span>
            </label>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <footer class="runner-footer">
        <span class="runner-answered">
          {{ answeredCount }} / {{ quiz.question_count }} respondidas
        </span>
        <button
          class="btn-submit"
          :disabled="!allAnswered || submitting"
          @click="handleSubmit"
        >
          <span v-if="submitting" class="spinner" />
          {{ submitting ? 'Entregando...' : 'Entregar Quiz' }}
        </button>
      </footer>

      <!-- Confirm dialog -->
      <div v-if="showConfirm" class="confirm-overlay">
        <div class="confirm-box">
          <p class="confirm-text">¿Seguro que querés entregar? No podrás cambiar tus respuestas.</p>
          <div class="confirm-actions">
            <button class="btn-cancel" @click="showConfirm = false">Cancelar</button>
            <button class="btn-confirm" :disabled="submitting" @click="confirmSubmit">
              <span v-if="submitting" class="spinner spinner--sm" />
              Sí, entregar
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Quiz } from '@/types/quizzes'
import QuizCodeBlock from './QuizCodeBlock.vue'

const props = defineProps<{ quiz: Quiz; submitting: boolean }>()
const emit = defineEmits<{
  close: []
  submitted: [answers: number[]]
}>()

const answers = ref<(number | undefined)[]>(
  Array(props.quiz.questions.length).fill(undefined),
)
const showConfirm = ref(false)

const answeredCount = computed(() => answers.value.filter(a => a !== undefined).length)
const allAnswered = computed(() => answeredCount.value === props.quiz.questions.length)
const progressPercent = computed(() =>
  props.quiz.question_count > 0
    ? Math.round((answeredCount.value / props.quiz.question_count) * 100)
    : 0,
)

function handleSubmit() {
  if (!allAnswered.value) return
  showConfirm.value = true
}

function confirmSubmit() {
  showConfirm.value = false
  emit('submitted', answers.value as number[])
}
</script>

<style scoped>
.runner-overlay {
  position: fixed;
  inset: 0;
  background: #00000088;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
  padding: 1rem;
}

.runner-modal {
  background: #1e1e2e;
  border: 1px solid #313244;
  border-radius: 12px;
  width: 100%;
  max-width: 720px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

/* Header */
.runner-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.25rem 1.5rem 1rem;
  border-bottom: 1px solid #313244;
  flex-shrink: 0;
}

.runner-header-left { display: flex; flex-direction: column; gap: 0.25rem; }

.runner-title {
  font-size: 1rem;
  font-weight: 700;
  color: #cdd6f4;
  margin: 0;
}

.runner-meta {
  font-size: 0.75rem;
  color: #6c7086;
}

.runner-close {
  background: transparent;
  border: none;
  color: #6c7086;
  font-size: 0.9rem;
  cursor: pointer;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  transition: color 0.15s;
  flex-shrink: 0;
}
.runner-close:hover { color: #f38ba8; }

/* Progress */
.runner-progress-bar {
  height: 3px;
  background: #313244;
  flex-shrink: 0;
}
.runner-progress-fill {
  height: 100%;
  background: #cba6f7;
  transition: width 0.3s ease;
}

/* Body */
.runner-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.question-block {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.question-number {
  font-size: 0.7rem;
  font-weight: 700;
  color: #cba6f7;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.question-text {
  font-size: 0.9rem;
  color: #cdd6f4;
  line-height: 1.55;
  white-space: pre-wrap;
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 0.25rem;
}

.option-label {
  display: flex;
  align-items: flex-start;
  gap: 0.65rem;
  padding: 0.65rem 0.9rem;
  background: #181825;
  border: 1px solid #313244;
  border-radius: 8px;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
}

.option-label:hover { border-color: #585b70; background: #1e1e2e; }

.option-label--selected {
  border-color: #cba6f7;
  background: #2a1f3d;
}

.option-radio { display: none; }

.option-text {
  font-size: 0.85rem;
  color: #cdd6f4;
  line-height: 1.45;
}

/* Footer */
.runner-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-top: 1px solid #313244;
  flex-shrink: 0;
  gap: 1rem;
}

.runner-answered {
  font-size: 0.78rem;
  color: #6c7086;
}

.btn-submit {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.55rem 1.4rem;
  background: #cba6f7;
  color: #1e1e2e;
  border: none;
  border-radius: 8px;
  font-family: inherit;
  font-size: 0.85rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.15s, opacity 0.15s;
}
.btn-submit:hover:not(:disabled) { background: #b794e0; }
.btn-submit:disabled { opacity: 0.45; cursor: not-allowed; }

/* Confirm */
.confirm-overlay {
  position: absolute;
  inset: 0;
  background: #00000088;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
}

.confirm-box {
  background: #181825;
  border: 1px solid #313244;
  border-radius: 10px;
  padding: 1.5rem;
  max-width: 380px;
  width: 90%;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.confirm-text {
  font-size: 0.88rem;
  color: #cdd6f4;
  line-height: 1.5;
  margin: 0;
}

.confirm-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

.btn-cancel {
  padding: 0.45rem 1rem;
  background: transparent;
  border: 1px solid #313244;
  border-radius: 7px;
  color: #6c7086;
  font-family: inherit;
  font-size: 0.82rem;
  cursor: pointer;
  transition: border-color 0.15s, color 0.15s;
}
.btn-cancel:hover { border-color: #585b70; color: #a6adc8; }

.btn-confirm {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
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
.btn-confirm:hover:not(:disabled) { background: #b794e0; }
.btn-confirm:disabled { opacity: 0.5; cursor: not-allowed; }

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
</style>