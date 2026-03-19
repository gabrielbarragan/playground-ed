<template>
  <div class="ch-desc">
    <!-- Header -->
    <div class="ch-header">
      <div class="ch-header-top">
        <span class="diff-badge" :class="`diff--${challenge.difficulty}`">
          {{ diffLabel(challenge.difficulty) }}
        </span>
        <span class="ch-pts">{{ challenge.points }} pts base</span>
        <span v-if="challenge.requires_review" class="ch-review-tag">Revisión manual</span>
        <span
          v-if="challenge.required_functions?.length"
          class="ch-fn-tag"
          :title="'Funciones requeridas: ' + challenge.required_functions.join(', ')"
        >
          def {{ challenge.required_functions.join(', ') }}
        </span>
      </div>
      <h2 class="ch-title">{{ challenge.title }}</h2>
      <div v-if="challenge.courses?.length" class="ch-courses">
        <span v-for="c in challenge.courses" :key="c.id" class="ch-course-badge">{{ c.code }}</span>
      </div>
    </div>

    <div class="ch-body">
      <!-- Description -->
      <div class="ch-section">
        <span class="ch-section-label">Descripción</span>
        <div class="ch-text ch-markdown" v-html="descriptionHtml" />
      </div>

      <!-- Example I/O -->
      <div v-if="challenge.example_input || challenge.example_output" class="ch-examples">
        <div v-if="challenge.example_input" class="ch-example">
          <span class="ch-section-label">Ejemplo de entrada</span>
          <pre class="ch-code-block">{{ challenge.example_input }}</pre>
        </div>
        <div v-if="challenge.example_output" class="ch-example">
          <span class="ch-section-label">Salida esperada</span>
          <pre class="ch-code-block">{{ challenge.example_output }}</pre>
        </div>
      </div>

      <!-- Tags -->
      <div v-if="challenge.tags?.length" class="ch-tags">
        <span v-for="tag in challenge.tags" :key="tag" class="ch-tag">{{ tag }}</span>
      </div>

      <!-- Error de validación AST (funciones no definidas) -->
      <div v-if="lastAttempt?.ast_validation_error" class="ch-ast-error">
        <span class="ch-ast-icon">⚠️</span>
        <span class="ch-ast-msg">{{ lastAttempt.ast_validation_error }}</span>
      </div>

      <!-- Last attempt result -->
      <div v-if="lastAttempt && !lastAttempt.ast_validation_error" class="ch-attempt-result" :class="attemptClass">
        <div class="ch-attempt-header">
          <span class="ch-attempt-icon">{{ attemptIcon }}</span>
          <span class="ch-attempt-title">{{ attemptTitle }}</span>
          <span class="ch-attempt-pts" v-if="lastAttempt.points_earned">
            +{{ lastAttempt.points_earned }} pts
          </span>
        </div>

        <!-- Feedback de bono de líneas -->
        <div v-if="challenge.lines_bonus_points && lastAttempt.passed" class="ch-bonus-row">
          <template v-if="lastAttempt.bonus_points_earned > 0">
            <span class="ch-bonus-icon">🎯</span>
            <span class="ch-bonus-text">
              Bono de eficiencia: <strong>+{{ lastAttempt.bonus_points_earned }} pts</strong>
              — {{ lastAttempt.effective_lines }} líneas (rango óptimo: {{ challenge.optimal_lines_min }}–{{ challenge.optimal_lines_max }})
            </span>
          </template>
          <template v-else>
            <span class="ch-bonus-icon">💡</span>
            <span class="ch-bonus-text ch-bonus-text--miss">
              Tu solución tiene {{ lastAttempt.effective_lines }} línea{{ lastAttempt.effective_lines !== 1 ? 's' : '' }}.
              El rango óptimo es {{ challenge.optimal_lines_min }}–{{ challenge.optimal_lines_max }} — sin bono esta vez.
            </span>
          </template>
        </div>

        <!-- Test case results -->
        <div v-if="lastAttempt.results?.length" class="ch-tc-results">
          <div
            v-for="(r, i) in lastAttempt.results" :key="i"
            class="ch-tc-item"
            :class="r.passed ? 'ch-tc--pass' : 'ch-tc--fail'"
          >
            <div class="ch-tc-row">
              <span class="ch-tc-icon">{{ r.passed ? '✓' : '✗' }}</span>
              <span class="ch-tc-label">Test {{ i + 1 }}</span>
            </div>
            <div v-if="r.actual_output" class="ch-tc-output">
              <span class="ch-tc-output-label">Tu output</span>
              <pre class="ch-tc-pre">{{ r.actual_output }}</pre>
            </div>
            <div v-if="r.error" class="ch-tc-output">
              <span class="ch-tc-output-label ch-tc-output-label--err">Error</span>
              <pre class="ch-tc-pre ch-tc-pre--err">{{ r.error }}</pre>
            </div>
          </div>
        </div>

        <p v-if="lastAttempt.review_feedback" class="ch-feedback">
          {{ lastAttempt.review_feedback }}
        </p>

        <div v-if="lastAttempt.review_status === 'pending'" class="ch-pending-note">
          Tu solución está esperando revisión del docente.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'
import type { Challenge, Attempt } from '@/types/challenges'

const props = defineProps<{
  challenge: Challenge
  lastAttempt: Attempt | null
}>()

const descriptionHtml = computed(() =>
  marked(props.challenge.description ?? '', { breaks: true }) as string,
)

function diffLabel(d: string) {
  return d === 'easy' ? 'Fácil' : d === 'medium' ? 'Media' : 'Difícil'
}

const attemptClass = computed(() => {
  const a = props.lastAttempt
  if (!a) return ''
  if (a.passed) return 'ch-attempt--passed'
  if (a.review_status === 'pending') return 'ch-attempt--pending'
  if (a.review_status === 'rejected') return 'ch-attempt--rejected'
  return 'ch-attempt--failed'
})

const attemptIcon = computed(() => {
  const a = props.lastAttempt
  if (!a) return ''
  if (a.passed) return '✓'
  if (a.review_status === 'pending') return '⏳'
  if (a.review_status === 'rejected') return '✗'
  return '✗'
})

const attemptTitle = computed(() => {
  const a = props.lastAttempt
  if (!a) return ''
  if (a.passed) return 'Correcto'
  if (a.review_status === 'pending') return 'Enviado — pendiente de revisión'
  if (a.review_status === 'rejected') return 'Rechazado'
  return `Fallido — intento #${a.attempt_number}`
})
</script>

<style scoped>
.ch-desc {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  overflow: hidden;
  background: #1e1e2e;
  font-family: 'JetBrains Mono', monospace;
}

.ch-header {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid #313244;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.ch-header-top {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.diff-badge {
  font-size: 0.65rem;
  padding: 0.12rem 0.5rem;
  border-radius: 4px;
  font-weight: 700;
}
.diff--easy   { background: #1e3a1e; color: #a6e3a1; }
.diff--medium { background: #3a2a1e; color: #fab387; }
.diff--hard   { background: #3a1e1e; color: #f38ba8; }

.ch-pts {
  font-size: 0.7rem;
  color: #f9e2af;
  font-weight: 600;
}

.ch-review-tag {
  font-size: 0.65rem;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  background: #89b4fa20;
  color: #89b4fa;
  font-weight: 600;
}

.ch-title {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 700;
  color: #cdd6f4;
}

.ch-courses {
  display: flex;
  gap: 0.35rem;
  flex-wrap: wrap;
}

.ch-course-badge {
  font-size: 0.62rem;
  padding: 0.08rem 0.4rem;
  border-radius: 3px;
  background: #313244;
  color: #cba6f7;
  font-weight: 700;
}

.ch-body {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  min-width: 0;
  max-width: 100%;
  padding: 0.85rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.ch-body::-webkit-scrollbar { width: 4px; }
.ch-body::-webkit-scrollbar-track { background: transparent; }
.ch-body::-webkit-scrollbar-thumb { background: #313244; border-radius: 2px; }

.ch-section { display: flex; flex-direction: column; gap: 0.4rem; }

.ch-section-label {
  font-size: 0.65rem;
  font-weight: 700;
  color: #45475a;
  text-transform: uppercase;
  letter-spacing: 0.07em;
}

.ch-text {
  font-size: 0.8rem;
  color: #a6adc8;
  white-space: pre-wrap;
  word-break: break-word;
  overflow-wrap: break-word;
  line-height: 1.6;
  margin: 0;
  min-width: 0;
  max-width: 100%;
  font-family: 'JetBrains Mono', monospace;
}

/* ── Markdown description styles ─────────────────────────── */
.ch-markdown {
  min-width: 0;
  max-width: 100%;
  overflow-wrap: break-word;
  word-break: break-word;
}

.ch-markdown :deep(*) {
  max-width: 100%;
  overflow-wrap: break-word;
  word-break: break-word;
}

.ch-markdown :deep(p) {
  margin: 0 0 0.6em;
  line-height: 1.6;
  white-space: normal;
}
.ch-markdown :deep(p:last-child) { margin-bottom: 0; }

.ch-markdown :deep(strong) { color: #cdd6f4; font-weight: 700; }
.ch-markdown :deep(em) { color: #cdd6f4; font-style: italic; }

.ch-markdown :deep(code) {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.78em;
  background: #11111b;
  border: 1px solid #313244;
  border-radius: 4px;
  padding: 0.1em 0.35em;
  color: #cba6f7;
}

.ch-markdown :deep(pre) {
  background: #11111b;
  border: 1px solid #313244;
  border-radius: 6px;
  padding: 0.6rem 0.75rem;
  overflow-x: auto;
  overflow-y: hidden;
  max-width: 100%;
  margin: 0.5em 0;
  white-space: pre;
  word-break: normal;
  overflow-wrap: normal;
}
.ch-markdown :deep(pre code) {
  background: none;
  border: none;
  padding: 0;
  color: #cdd6f4;
  font-size: 0.78rem;
  white-space: pre;
  word-break: normal;
  overflow-wrap: normal;
}

.ch-markdown :deep(ul),
.ch-markdown :deep(ol) {
  margin: 0.4em 0 0.6em 1.25em;
  padding: 0;
  line-height: 1.6;
}
.ch-markdown :deep(li) { margin-bottom: 0.2em; }

.ch-markdown :deep(h1),
.ch-markdown :deep(h2),
.ch-markdown :deep(h3) {
  color: #cdd6f4;
  font-weight: 700;
  margin: 0.75em 0 0.35em;
  line-height: 1.3;
}
.ch-markdown :deep(h1) { font-size: 1em; }
.ch-markdown :deep(h2) { font-size: 0.92em; }
.ch-markdown :deep(h3) { font-size: 0.85em; }

.ch-markdown :deep(blockquote) {
  border-left: 3px solid #cba6f7;
  margin: 0.5em 0;
  padding: 0.25em 0.75em;
  color: #6c7086;
  font-style: italic;
}

.ch-markdown :deep(hr) {
  border: none;
  border-top: 1px solid #313244;
  margin: 0.75em 0;
}

.ch-examples {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.ch-example { display: flex; flex-direction: column; gap: 0.35rem; }

.ch-code-block {
  background: #11111b;
  border: 1px solid #313244;
  border-radius: 6px;
  padding: 0.6rem 0.75rem;
  font-size: 0.78rem;
  color: #cdd6f4;
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
  font-family: 'JetBrains Mono', monospace;
}

.ch-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.ch-tag {
  font-size: 0.65rem;
  padding: 0.1rem 0.45rem;
  border-radius: 4px;
  background: #313244;
  color: #6c7086;
}

/* ── Attempt result ───────────────────────────────────────── */
.ch-attempt-result {
  border-radius: 8px;
  border: 1px solid #313244;
  padding: 0.75rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.ch-attempt--passed  { border-color: #a6e3a140; background: #a6e3a108; }
.ch-attempt--pending { border-color: #fab38740; background: #fab38708; }
.ch-attempt--rejected { border-color: #f38ba840; background: #f38ba808; }
.ch-attempt--failed  { border-color: #f38ba840; background: #f38ba808; }

.ch-attempt-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.ch-attempt-icon {
  font-size: 0.85rem;
}

.ch-attempt--passed  .ch-attempt-icon { color: #a6e3a1; }
.ch-attempt--pending .ch-attempt-icon { color: #fab387; }
.ch-attempt--rejected .ch-attempt-icon,
.ch-attempt--failed  .ch-attempt-icon { color: #f38ba8; }

.ch-attempt-title {
  font-size: 0.8rem;
  font-weight: 700;
  color: #cdd6f4;
}

.ch-attempt-pts {
  margin-left: auto;
  font-size: 0.75rem;
  font-weight: 700;
  color: #f9e2af;
}

.ch-tc-results {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.ch-tc-item {
  border-radius: 6px;
  padding: 0.5rem 0.65rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}
.ch-tc--pass { background: #a6e3a110; border: 1px solid #a6e3a125; }
.ch-tc--fail { background: #f38ba810; border: 1px solid #f38ba825; }

.ch-tc-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
}

.ch-tc-icon { font-size: 0.7rem; width: 14px; text-align: center; }
.ch-tc--pass .ch-tc-icon { color: #a6e3a1; }
.ch-tc--fail .ch-tc-icon { color: #f38ba8; }

.ch-tc-label { color: #a6adc8; font-weight: 600; }

.ch-tc-output {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}
.ch-tc-output-label {
  font-size: 0.62rem;
  color: #6c7086;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.ch-tc-output-label--err { color: #f38ba8; }

.ch-tc-pre {
  margin: 0;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  color: #cdd6f4;
  background: #11111b;
  padding: 0.3rem 0.5rem;
  border-radius: 4px;
  white-space: pre-wrap;
  word-break: break-word;
}
.ch-tc-pre--err { color: #f38ba8; }

.ch-feedback {
  margin: 0;
  font-size: 0.78rem;
  color: #a6adc8;
  font-style: italic;
  border-top: 1px solid #313244;
  padding-top: 0.5rem;
}

.ch-pending-note {
  font-size: 0.75rem;
  color: #fab387;
  font-style: italic;
}

/* ── Funciones requeridas ─────────────────────────────── */
.ch-fn-tag {
  font-size: 0.65rem;
  padding: 0.1rem 0.45rem;
  border-radius: 4px;
  background: #1e2535;
  color: #89b4fa;
  font-weight: 600;
  font-family: 'JetBrains Mono', monospace;
  border: 1px solid #89b4fa30;
}

/* ── Error AST ────────────────────────────────────────── */
.ch-ast-error {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 0.65rem 0.85rem;
  border-radius: 8px;
  background: #2a1a1a;
  border: 1px solid #f38ba840;
  font-size: 0.78rem;
}

.ch-ast-icon { flex-shrink: 0; font-size: 0.9rem; }

.ch-ast-msg {
  color: #f38ba8;
  line-height: 1.5;
  font-family: 'JetBrains Mono', monospace;
}

/* ── Bonus de líneas ──────────────────────────────────── */
.ch-bonus-row {
  display: flex;
  align-items: flex-start;
  gap: 0.4rem;
  padding: 0.45rem 0.6rem;
  border-radius: 6px;
  background: #1e2a1e;
  border: 1px solid #a6e3a125;
  font-size: 0.75rem;
}

.ch-bonus-icon { flex-shrink: 0; font-size: 0.8rem; }

.ch-bonus-text { color: #a6e3a1; line-height: 1.4; }
.ch-bonus-text strong { color: #a6e3a1; }

.ch-bonus-text--miss {
  color: #6c7086;
  background: transparent;
}

.ch-bonus-row:has(.ch-bonus-text--miss) {
  background: #1e1e2e;
  border-color: #313244;
}
</style>