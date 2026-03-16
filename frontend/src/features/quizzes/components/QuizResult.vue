<template>
  <div class="result-overlay" @click.self="$emit('close')">
    <div class="result-modal">
      <!-- Header -->
      <header class="result-header">
        <h2 class="result-title">Resultado del Quiz</h2>
        <button class="result-close" @click="$emit('close')">✕</button>
      </header>

      <!-- Summary -->
      <div class="result-summary" :class="attempt.passed ? 'summary--pass' : 'summary--fail'">
        <div class="summary-icon">{{ attempt.passed ? '✓' : '✗' }}</div>
        <div class="summary-info">
          <div class="summary-status">{{ attempt.passed ? 'Aprobado' : 'No aprobado' }}</div>
          <div class="summary-score">
            {{ attempt.correct_count }} / {{ attempt.total_questions }} correctas
          </div>
          <div v-if="attempt.points_earned > 0" class="summary-points">
            +{{ attempt.points_earned }} puntos
          </div>
        </div>
      </div>

      <!-- Correction detail (solo si show_correct_answers=true) -->
      <div v-if="attempt.questions?.length" class="result-body">
        <div
          v-for="q in attempt.questions"
          :key="q.index"
          class="result-question"
          :class="q.is_correct ? 'rq--correct' : 'rq--wrong'"
        >
          <div class="rq-header">
            <span class="rq-num">Pregunta {{ q.index + 1 }}</span>
            <span class="rq-badge" :class="q.is_correct ? 'rq-badge--ok' : 'rq-badge--fail'">
              {{ q.is_correct ? '✓ Correcta' : '✗ Incorrecta' }}
            </span>
          </div>
          <div class="rq-text">{{ q.text }}</div>
          <QuizCodeBlock v-if="q.code_block" :code="q.code_block" />
          <div class="rq-options">
            <div
              v-for="(opt, j) in q.options"
              :key="j"
              class="rq-option"
              :class="{
                'rq-option--correct': j === q.correct_option_index,
                'rq-option--selected-wrong': j === q.selected_option_index && !q.is_correct,
              }"
            >
              <span class="rq-option-icon">
                <template v-if="j === q.correct_option_index">✓</template>
                <template v-else-if="j === q.selected_option_index && !q.is_correct">✗</template>
                <template v-else>·</template>
              </span>
              {{ opt.text }}
            </div>
          </div>
          <div v-if="q.explanation" class="rq-explanation">
            {{ q.explanation }}
          </div>
        </div>
      </div>

      <footer class="result-footer">
        <button class="btn-close-result" @click="$emit('close')">Cerrar</button>
      </footer>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { QuizAttempt } from '@/types/quizzes'
import QuizCodeBlock from './QuizCodeBlock.vue'

defineProps<{ attempt: QuizAttempt }>()
defineEmits<{ close: [] }>()
</script>

<style scoped>
.result-overlay {
  position: fixed;
  inset: 0;
  background: #00000088;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
  padding: 1rem;
}

.result-modal {
  background: #1e1e2e;
  border: 1px solid #313244;
  border-radius: 12px;
  width: 100%;
  max-width: 680px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Header */
.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #313244;
  flex-shrink: 0;
}

.result-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #cdd6f4;
  margin: 0;
}

.result-close {
  background: transparent;
  border: none;
  color: #6c7086;
  font-size: 0.9rem;
  cursor: pointer;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  transition: color 0.15s;
}
.result-close:hover { color: #f38ba8; }

/* Summary */
.result-summary {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #313244;
  flex-shrink: 0;
}

.summary--pass { background: #1e3a2a; }
.summary--fail { background: #3a1e1e; }

.summary-icon {
  font-size: 2rem;
  font-weight: 700;
  line-height: 1;
}
.summary--pass .summary-icon { color: #a6e3a1; }
.summary--fail .summary-icon { color: #f38ba8; }

.summary-info { display: flex; flex-direction: column; gap: 0.2rem; }

.summary-status {
  font-size: 1rem;
  font-weight: 700;
}
.summary--pass .summary-status { color: #a6e3a1; }
.summary--fail .summary-status { color: #f38ba8; }

.summary-score {
  font-size: 0.85rem;
  color: #a6adc8;
}

.summary-points {
  font-size: 0.82rem;
  color: #f9e2af;
  font-weight: 600;
}

/* Body */
.result-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.result-question {
  background: #181825;
  border: 1px solid #313244;
  border-radius: 10px;
  padding: 1rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  border-left-width: 3px;
}
.rq--correct { border-left-color: #a6e3a1; }
.rq--wrong   { border-left-color: #f38ba8; }

.rq-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.rq-num {
  font-size: 0.7rem;
  font-weight: 700;
  color: #6c7086;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.rq-badge {
  font-size: 0.7rem;
  font-weight: 700;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
}
.rq-badge--ok   { background: #a6e3a120; color: #a6e3a1; }
.rq-badge--fail { background: #f38ba820; color: #f38ba8; }

.rq-text {
  font-size: 0.88rem;
  color: #cdd6f4;
  line-height: 1.5;
  white-space: pre-wrap;
}

.rq-options {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.rq-option {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  font-size: 0.83rem;
  color: #a6adc8;
  background: #1e1e2e;
  border: 1px solid #313244;
}

.rq-option--correct {
  background: #1e3a2a;
  border-color: #a6e3a140;
  color: #a6e3a1;
  font-weight: 600;
}

.rq-option--selected-wrong {
  background: #3a1e1e;
  border-color: #f38ba840;
  color: #f38ba8;
}

.rq-option-icon {
  font-weight: 700;
  min-width: 14px;
  line-height: 1.45;
  flex-shrink: 0;
}

.rq-explanation {
  font-size: 0.8rem;
  color: #89b4fa;
  background: #1a2030;
  border: 1px solid #89b4fa30;
  border-radius: 6px;
  padding: 0.65rem 0.85rem;
  line-height: 1.5;
}

/* Footer */
.result-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #313244;
  display: flex;
  justify-content: flex-end;
  flex-shrink: 0;
}

.btn-close-result {
  padding: 0.5rem 1.25rem;
  background: #313244;
  border: 1px solid #45475a;
  border-radius: 7px;
  color: #cdd6f4;
  font-family: inherit;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-close-result:hover { background: #45475a; }
</style>