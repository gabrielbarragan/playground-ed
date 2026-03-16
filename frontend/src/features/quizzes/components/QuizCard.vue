<template>
  <div class="quiz-card" :class="{ 'quiz-card--inactive': quiz.status === 'passed' }">
    <div class="qc-header">
      <span class="qc-status-badge" :class="`status--${quiz.status}`">
        {{ STATUS_LABEL[quiz.status] }}
      </span>
      <div class="qc-points">
        <span v-if="quiz.points_on_complete" class="qc-pts">{{ quiz.points_on_complete }} pts</span>
        <span v-if="quiz.points_on_pass" class="qc-pts qc-pts--bonus">+{{ quiz.points_on_pass }} bonus</span>
      </div>
    </div>

    <h3 class="qc-title">{{ quiz.title }}</h3>
    <p v-if="quiz.description" class="qc-description">{{ quiz.description }}</p>

    <div class="qc-meta">
      <span class="qc-meta-item">{{ quiz.question_count }} preguntas</span>
      <span class="qc-meta-sep">·</span>
      <span class="qc-meta-item">Aprobar con {{ quiz.passing_score }}</span>
    </div>

    <div class="qc-actions">
      <button
        v-if="quiz.status === 'pending'"
        class="btn-respond"
        @click="$emit('respond', quiz.id)"
      >
        Responder
      </button>
      <template v-else>
        <button class="btn-result" @click="$emit('viewResult', quiz.id)">Ver resultado</button>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { QuizProgress } from '@/types/quizzes'

defineProps<{ quiz: QuizProgress }>()
defineEmits<{
  respond: [id: string]
  viewResult: [id: string]
}>()

const STATUS_LABEL: Record<string, string> = {
  pending: 'Pendiente',
  completed: 'Entregado',
  passed: 'Aprobado',
}
</script>

<style scoped>
.quiz-card {
  background: #181825;
  border: 1px solid #313244;
  border-radius: 10px;
  padding: 1.1rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  transition: border-color 0.15s;
}
.quiz-card:hover { border-color: #45475a; }

.qc-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.qc-status-badge {
  font-size: 0.65rem;
  font-weight: 700;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.status--pending   { background: #45475a30; color: #a6adc8; }
.status--completed { background: #89b4fa20; color: #89b4fa; }
.status--passed    { background: #a6e3a120; color: #a6e3a1; }

.qc-points {
  display: flex;
  gap: 0.4rem;
  align-items: center;
}

.qc-pts {
  font-size: 0.7rem;
  color: #f9e2af;
  font-weight: 700;
}
.qc-pts--bonus { color: #a6e3a1; }

.qc-title {
  font-size: 0.92rem;
  font-weight: 700;
  color: #cdd6f4;
  margin: 0;
}

.qc-description {
  font-size: 0.8rem;
  color: #6c7086;
  margin: 0;
  line-height: 1.45;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.qc-meta {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  flex-wrap: wrap;
}

.qc-meta-item {
  font-size: 0.72rem;
  color: #6c7086;
}
.qc-meta-sep { color: #45475a; font-size: 0.72rem; }

.qc-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.25rem;
}

.btn-respond {
  flex: 1;
  padding: 0.45rem 1rem;
  background: #cba6f7;
  border: none;
  border-radius: 7px;
  color: #1e1e2e;
  font-family: inherit;
  font-size: 0.82rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-respond:hover { background: #b794e0; }

.btn-result {
  flex: 1;
  padding: 0.45rem 1rem;
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
.btn-result:hover { background: #45475a; }
</style>