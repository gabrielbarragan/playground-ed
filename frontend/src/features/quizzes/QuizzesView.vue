<template>
  <div class="quizzes-page">
    <!-- Header -->
    <header class="qv-header">
      <div class="qv-header-left">
        <RouterLink to="/" class="back-link">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
            <path d="M19 12H5M12 5l-7 7 7 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          Playground
        </RouterLink>
        <span class="qv-title">Evaluaciones</span>
      </div>
      <div class="qv-header-right">
        <span class="qv-chip">{{ auth.user?.first_name }} {{ auth.user?.last_name }}</span>
      </div>
    </header>

    <!-- Body -->
    <main class="qv-body">
      <div v-if="store.loading" class="qv-loading">
        <span class="big-spinner" />
        Cargando evaluaciones...
      </div>

      <template v-else>
        <div class="qv-toolbar">
          <h1 class="qv-section-title">
            Mis Evaluaciones
            <span class="qv-count">{{ store.quizzes.length }}</span>
          </h1>
        </div>

        <div v-if="!store.quizzes.length" class="qv-empty">
          No hay evaluaciones disponibles para tu curso por ahora.
        </div>

        <div v-else class="quizzes-grid">
          <QuizCard
            v-for="q in store.quizzes"
            :key="q.id"
            :quiz="q"
            @respond="handleRespond"
            @view-result="handleViewResult"
          />
        </div>
      </template>
    </main>

    <!-- Quiz Runner -->
    <QuizRunner
      v-if="showRunner && activeQuiz"
      :quiz="activeQuiz"
      :submitting="store.submitting"
      @close="showRunner = false"
      @submitted="handleSubmitted"
    />

    <!-- Quiz Result -->
    <QuizResult
      v-if="showResult && lastAttempt"
      :attempt="lastAttempt"
      @close="showResult = false"
    />

    <!-- Error toast -->
    <div v-if="errorMsg" class="error-toast">{{ errorMsg }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/useAuthStore'
import { useQuizzesStore } from '@/stores/useQuizzesStore'
import type { QuizAttempt } from '@/types/quizzes'
import QuizCard from './components/QuizCard.vue'
import QuizRunner from './components/QuizRunner.vue'
import QuizResult from './components/QuizResult.vue'

const auth = useAuthStore()
const store = useQuizzesStore()

const showRunner = ref(false)
const showResult = ref(false)
const errorMsg = ref('')

const activeQuiz = computed(() => store.activeQuiz)
const lastAttempt = computed(() => store.lastAttempt)

let errorTimer: ReturnType<typeof setTimeout>
function showError(msg: string) {
  errorMsg.value = msg
  clearTimeout(errorTimer)
  errorTimer = setTimeout(() => { errorMsg.value = '' }, 4000)
}

async function handleRespond(id: string) {
  try {
    await store.openQuiz(id)
    showRunner.value = true
  } catch {
    showError('No se pudo cargar el quiz.')
  }
}

async function handleViewResult(id: string) {
  try {
    await store.openResult(id)
    showResult.value = true
  } catch {
    showError('No se pudo cargar el resultado.')
  }
}

async function handleSubmitted(answers: number[]) {
  try {
    await store.submit(answers)
    showRunner.value = false
    showResult.value = true
  } catch (e: unknown) {
    const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    showError(msg ?? 'Error al entregar el quiz.')
  }
}

onMounted(() => store.fetchQuizzes())
</script>

<style scoped>
.quizzes-page {
  min-height: 100vh;
  background: #1e1e2e;
  color: #cdd6f4;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  display: flex;
  flex-direction: column;
}

/* Header */
.qv-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.5rem;
  height: 48px;
  background: #181825;
  border-bottom: 1px solid #313244;
  flex-shrink: 0;
}

.qv-header-left {
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

.qv-title {
  font-size: 0.9rem;
  font-weight: 700;
  color: #cdd6f4;
}

.qv-chip {
  font-size: 0.72rem;
  background: #313244;
  color: #cba6f7;
  padding: 0.15rem 0.6rem;
  border-radius: 4px;
}

/* Body */
.qv-body {
  flex: 1;
  max-width: 1100px;
  width: 100%;
  margin: 0 auto;
  padding: 2rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.qv-loading {
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

.qv-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.qv-section-title {
  font-size: 0.9rem;
  font-weight: 700;
  color: #a6adc8;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.qv-count {
  font-size: 0.72rem;
  background: #313244;
  color: #6c7086;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-weight: 400;
}

.qv-empty {
  text-align: center;
  padding: 3rem;
  color: #45475a;
  font-size: 0.85rem;
}

.quizzes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}

/* Error toast */
.error-toast {
  position: fixed;
  bottom: 1.5rem;
  left: 50%;
  transform: translateX(-50%);
  background: #f38ba820;
  border: 1px solid #f38ba850;
  color: #f38ba8;
  padding: 0.6rem 1.25rem;
  border-radius: 8px;
  font-size: 0.82rem;
  z-index: 300;
}

@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 700px) {
  .qv-body { padding: 1rem; }
  .quizzes-grid { grid-template-columns: 1fr; }
}
</style>