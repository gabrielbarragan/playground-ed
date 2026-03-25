<template>
  <div class="scp">
    <div v-if="loadingChallenges" class="scp-loading"><span class="spinner" /> Cargando...</div>

    <template v-else-if="challenges">
      <!-- Sub-tabs -->
      <div class="subtabs">
        <button
          class="subtab" :class="{ 'subtab--active': subTab === 'solved' }"
          @click="subTab = 'solved'"
        >
          Resueltos <span class="subtab-count">{{ challenges.solved.length }}</span>
        </button>
        <button
          class="subtab" :class="{ 'subtab--active': subTab === 'pending' }"
          @click="subTab = 'pending'"
        >
          Pendientes <span class="subtab-count">{{ challenges.pending.length }}</span>
        </button>
      </div>

      <!-- Resueltos -->
      <template v-if="subTab === 'solved'">
        <div v-if="!challenges.solved.length" class="scp-empty">No ha resuelto retos aún.</div>
        <table v-else class="ch-table">
          <thead>
            <tr>
              <th>Reto</th>
              <th>Dif.</th>
              <th>Pts ganados</th>
              <th>Bonus</th>
              <th>Intento</th>
              <th>Fecha</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in challenges.solved" :key="c.challenge_id">
              <td class="cell-title">{{ c.title }}</td>
              <td><span class="diff-chip" :class="`diff--${c.difficulty}`">{{ diffLabel(c.difficulty) }}</span></td>
              <td class="cell-pts">{{ c.points_earned }} <span class="cell-max">/ {{ c.points }}</span></td>
              <td class="cell-bonus">
                <span v-if="c.bonus_points_earned" class="bonus-tag">+{{ c.bonus_points_earned }}</span>
                <span v-else class="cell-null">—</span>
              </td>
              <td class="cell-center">#{{ c.attempt_number }}</td>
              <td class="cell-date">{{ fmtDate(c.solved_at) }}</td>
            </tr>
          </tbody>
        </table>
      </template>

      <!-- Pendientes -->
      <template v-if="subTab === 'pending'">
        <div v-if="!challenges.pending.length" class="scp-empty">Ha resuelto todos los retos del curso.</div>
        <table v-else class="ch-table">
          <thead>
            <tr>
              <th>Reto</th>
              <th>Dif.</th>
              <th>Pts disponibles</th>
              <th>Intentos fallidos</th>
              <th>Tipo</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in challenges.pending" :key="c.challenge_id">
              <td class="cell-title">{{ c.title }}</td>
              <td><span class="diff-chip" :class="`diff--${c.difficulty}`">{{ diffLabel(c.difficulty) }}</span></td>
              <td class="cell-pts">{{ c.points }}</td>
              <td class="cell-center">
                <span :class="c.total_attempts > 3 ? 'attempts-high' : 'attempts-normal'">
                  {{ c.total_attempts }}
                </span>
              </td>
              <td>
                <span v-if="c.requires_review" class="review-chip">Manual</span>
                <span v-else class="auto-chip">Auto</span>
              </td>
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
const { challenges, loadingChallenges } = storeToRefs(store)
const subTab = ref<'solved' | 'pending'>('solved')

onMounted(() => store.loadChallenges())

function diffLabel(d: string) {
  return d === 'easy' ? 'Fácil' : d === 'medium' ? 'Media' : 'Difícil'
}

function fmtDate(iso: string) {
  return new Date(iso).toLocaleDateString('es-AR', { day: '2-digit', month: 'short', year: 'numeric' })
}
</script>

<style scoped>
.scp { display: flex; flex-direction: column; gap: 1rem; }
.scp-loading { display: flex; align-items: center; gap: 0.5rem; color: #6c7086; font-size: 0.85rem; padding: 1rem; }
.scp-empty { font-size: 0.85rem; color: #6c7086; padding: 0.5rem 0; }

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

.ch-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
.ch-table th {
  text-align: left; padding: 0.3rem 0.5rem;
  color: #6c7086; font-weight: 500; border-bottom: 1px solid #313244;
}
.ch-table td { padding: 0.4rem 0.5rem; border-bottom: 1px solid #1e1e2e; color: #cdd6f4; }

.cell-title { max-width: 160px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.cell-pts { font-weight: 600; color: #a6e3a1; }
.cell-max { font-weight: 400; color: #6c7086; font-size: 0.75rem; }
.cell-center { text-align: center; }
.cell-date { color: #6c7086; white-space: nowrap; font-size: 0.78rem; }
.cell-bonus { color: #f9e2af; }
.cell-null { color: #45475a; }

.bonus-tag { font-size: 0.78rem; color: #f9e2af; }

.diff-chip {
  font-size: 0.72rem; font-weight: 600; padding: 0.1rem 0.4rem; border-radius: 4px;
}
.diff--easy { background: rgba(166,227,161,0.15); color: #a6e3a1; }
.diff--medium { background: rgba(249,226,175,0.15); color: #f9e2af; }
.diff--hard { background: rgba(243,139,168,0.15); color: #f38ba8; }

.attempts-high { color: #f38ba8; font-weight: 700; }
.attempts-normal { color: #cdd6f4; }

.review-chip {
  font-size: 0.72rem; padding: 0.1rem 0.4rem; border-radius: 4px;
  background: rgba(203,166,247,0.15); color: #cba6f7;
}
.auto-chip {
  font-size: 0.72rem; padding: 0.1rem 0.4rem; border-radius: 4px;
  background: rgba(137,180,250,0.15); color: #89b4fa;
}
</style>
