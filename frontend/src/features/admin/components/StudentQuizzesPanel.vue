<template>
  <div class="sqp">
    <div v-if="loadingQuizzes" class="sqp-loading"><span class="spinner" /> Cargando...</div>

    <template v-else-if="quizzes">
      <div class="subtabs">
        <button
          class="subtab" :class="{ 'subtab--active': subTab === 'completed' }"
          @click="subTab = 'completed'"
        >
          Completados <span class="subtab-count">{{ quizzes.completed.length }}</span>
        </button>
        <button
          class="subtab" :class="{ 'subtab--active': subTab === 'pending' }"
          @click="subTab = 'pending'"
        >
          Pendientes <span class="subtab-count">{{ quizzes.pending.length }}</span>
        </button>
      </div>

      <!-- Completados -->
      <template v-if="subTab === 'completed'">
        <div v-if="!quizzes.completed.length" class="sqp-empty">No ha completado quizzes aún.</div>
        <table v-else class="qz-table">
          <thead>
            <tr>
              <th>Quiz</th>
              <th>Score</th>
              <th>Resultado</th>
              <th>Pts ganados</th>
              <th>Fecha</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="q in quizzes.completed" :key="q.quiz_id">
              <td class="cell-title">{{ q.title }}</td>
              <td class="cell-score">{{ q.correct_count }}/{{ q.total_questions }}</td>
              <td>
                <span class="result-chip" :class="q.passed ? 'result--pass' : 'result--fail'">
                  {{ q.passed ? 'Aprobado' : 'No aprobado' }}
                </span>
              </td>
              <td class="cell-pts">{{ q.points_earned }}</td>
              <td class="cell-date">{{ fmtDate(q.submitted_at) }}</td>
            </tr>
          </tbody>
        </table>
      </template>

      <!-- Pendientes -->
      <template v-if="subTab === 'pending'">
        <div v-if="!quizzes.pending.length" class="sqp-empty">Ha completado todos los quizzes del curso.</div>
        <table v-else class="qz-table">
          <thead>
            <tr>
              <th>Quiz</th>
              <th>Preguntas</th>
              <th>Pts por completar</th>
              <th>Pts por aprobar</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="q in quizzes.pending" :key="q.quiz_id">
              <td class="cell-title">{{ q.title }}</td>
              <td class="cell-center">{{ q.question_count }}</td>
              <td class="cell-pts">{{ q.points_on_complete }}</td>
              <td class="cell-pts">{{ q.points_on_pass }}</td>
            </tr>
          </tbody>
        </table>
      </template>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useStudentProfileStore } from '@/stores/useStudentProfileStore'
import { storeToRefs } from 'pinia'

const store = useStudentProfileStore()
const { quizzes, loadingQuizzes } = storeToRefs(store)
const subTab = ref<'completed' | 'pending'>('completed')

onMounted(() => store.loadQuizzes())

function fmtDate(iso: string) {
  return new Date(iso).toLocaleDateString('es-AR', { day: '2-digit', month: 'short', year: 'numeric' })
}
</script>

<style scoped>
.sqp { display: flex; flex-direction: column; gap: 1rem; }
.sqp-loading { display: flex; align-items: center; gap: 0.5rem; color: #6c7086; font-size: 0.85rem; padding: 1rem; }
.sqp-empty { font-size: 0.85rem; color: #6c7086; padding: 0.5rem 0; }

.subtabs { display: flex; gap: 0.25rem; border-bottom: 1px solid #313244; padding-bottom: 0.5rem; }
.subtab {
  background: none; border: none; color: #6c7086; font-size: 0.85rem;
  cursor: pointer; padding: 0.3rem 0.7rem; border-radius: 6px; display: flex; align-items: center; gap: 0.4rem;
}
.subtab:hover { color: #cdd6f4; background: #313244; }
.subtab--active { color: #cba6f7; background: rgba(203,166,247,0.1); }
.subtab-count {
  font-size: 0.72rem; background: #313244; color: #6c7086;
  padding: 0.1rem 0.4rem; border-radius: 999px;
}

.qz-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
.qz-table th {
  text-align: left; padding: 0.3rem 0.5rem;
  color: #6c7086; font-weight: 500; border-bottom: 1px solid #313244;
}
.qz-table td { padding: 0.4rem 0.5rem; border-bottom: 1px solid #1e1e2e; color: #cdd6f4; }

.cell-title { max-width: 180px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.cell-score { font-weight: 600; color: #cdd6f4; }
.cell-pts { font-weight: 600; color: #a6e3a1; }
.cell-center { text-align: center; }
.cell-date { color: #6c7086; white-space: nowrap; font-size: 0.78rem; }

.result-chip {
  font-size: 0.72rem; font-weight: 600; padding: 0.15rem 0.5rem; border-radius: 999px;
}
.result--pass { background: rgba(166,227,161,0.15); color: #a6e3a1; }
.result--fail { background: rgba(243,139,168,0.15); color: #f38ba8; }
</style>
