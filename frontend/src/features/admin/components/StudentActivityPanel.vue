<template>
  <div class="sap">
    <!-- Heatmap -->
    <div class="sap-section">
      <h3 class="sap-title">Actividad (últimos 15 días)</h3>
      <div class="heatmap">
        <div
          v-for="day in summary.activity_heatmap"
          :key="day.date"
          class="hm-cell"
          :class="heatClass(day.executions)"
          :title="`${day.date}: ${day.executions} ejecuciones`"
        />
      </div>
    </div>

    <!-- Puntos por día -->
    <div class="sap-section">
      <h3 class="sap-title">
        Puntos esta semana
        <span class="sap-total">+{{ breakdown?.total_week ?? 0 }} pts</span>
      </h3>

      <div v-if="loadingPoints" class="sap-loading"><span class="spinner" /></div>

      <div v-else-if="breakdown" class="bars-wrap">
        <div v-for="day in breakdown.days" :key="day.date" class="bar-col">
          <div class="bar-stack" :title="`${fmtDay(day.date)}: ${day.total} pts`">
            <div
              v-if="day.challenges" class="bar-seg bar-seg--challenges"
              :style="{ height: pct(day.challenges) + '%' }"
            />
            <div
              v-if="day.quizzes" class="bar-seg bar-seg--quizzes"
              :style="{ height: pct(day.quizzes) + '%' }"
            />
            <div
              v-if="day.bonus" class="bar-seg bar-seg--bonus"
              :style="{ height: pct(day.bonus) + '%' }"
            />
          </div>
          <span class="bar-label">{{ fmtDay(day.date) }}</span>
        </div>
      </div>

      <div class="bars-legend">
        <span class="legend-item"><span class="legend-dot legend-dot--challenges" />Retos</span>
        <span class="legend-item"><span class="legend-dot legend-dot--quizzes" />Quizzes</span>
        <span class="legend-item"><span class="legend-dot legend-dot--bonus" />Bonus</span>
      </div>
    </div>

    <!-- Últimas entregas -->
    <div class="sap-section">
      <h3 class="sap-title">Últimas entregas</h3>
      <div v-if="!summary.recent_attempts.length" class="sap-empty">Sin entregas aún.</div>
      <table v-else class="attempts-table">
        <thead>
          <tr>
            <th>Reto</th>
            <th>Dif.</th>
            <th>Intento</th>
            <th>Pts</th>
            <th>Estado</th>
            <th>Fecha</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="a in summary.recent_attempts" :key="a.id">
            <td class="cell-title">{{ a.challenge_title }}</td>
            <td><span class="diff-chip" :class="`diff--${a.challenge_difficulty}`">{{ diffLabel(a.challenge_difficulty) }}</span></td>
            <td class="cell-center">#{{ a.attempt_number }}</td>
            <td class="cell-pts">
              {{ a.points_earned }}
              <span v-if="a.bonus_points_earned" class="bonus-tag">+{{ a.bonus_points_earned }}</span>
            </td>
            <td>
              <span v-if="a.review_status === 'pending'" class="status-chip status--pending">Pendiente</span>
              <span v-else-if="a.passed" class="status-chip status--ok">✓</span>
              <span v-else class="status-chip status--fail">✗</span>
            </td>
            <td class="cell-date">{{ fmtDate(a.submitted_at) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useStudentProfileStore } from '@/stores/useStudentProfileStore'
import { storeToRefs } from 'pinia'

const props = defineProps<{ summary: any }>()
const store = useStudentProfileStore()
const { breakdown, loadingPoints } = storeToRefs(store)

onMounted(() => store.loadPointsBreakdown())

const maxPts = () => Math.max(1, ...((breakdown.value?.days ?? []).map((d: any) => d.total)))
const pct = (val: number) => Math.round((val / maxPts()) * 100)

function heatClass(n: number) {
  if (n === 0) return 'hm-0'
  if (n < 5) return 'hm-1'
  if (n < 15) return 'hm-2'
  return 'hm-3'
}

function fmtDay(iso: string) {
  return new Date(iso + 'T00:00:00').toLocaleDateString('es-AR', { weekday: 'short' })
}

function fmtDate(iso: string) {
  return new Date(iso).toLocaleDateString('es-AR', { day: '2-digit', month: 'short' })
}

function diffLabel(d: string) {
  return d === 'easy' ? 'F' : d === 'medium' ? 'M' : 'D'
}
</script>

<style scoped>
.sap { display: flex; flex-direction: column; gap: 1.5rem; }

.sap-section { display: flex; flex-direction: column; gap: 0.6rem; }

.sap-title {
  margin: 0; font-size: 0.85rem; font-weight: 600;
  color: #a6adc8; text-transform: uppercase; letter-spacing: 0.04em;
  display: flex; align-items: center; gap: 0.5rem;
}

.sap-total { font-size: 0.9rem; color: #a6e3a1; font-weight: 700; text-transform: none; letter-spacing: 0; }

.sap-loading { display: flex; justify-content: center; padding: 1rem; }
.sap-empty { font-size: 0.85rem; color: #6c7086; }

/* Heatmap */
.heatmap {
  display: flex; gap: 3px; flex-wrap: wrap;
}
.hm-cell {
  width: 14px; height: 14px; border-radius: 2px;
}
.hm-0 { background: #313244; }
.hm-1 { background: rgba(166,227,161,0.3); }
.hm-2 { background: rgba(166,227,161,0.6); }
.hm-3 { background: #a6e3a1; }

/* Barras */
.bars-wrap {
  display: flex; align-items: flex-end; gap: 4px; height: 80px;
}
.bar-col {
  display: flex; flex-direction: column; align-items: center; gap: 4px;
  flex: 1;
}
.bar-stack {
  flex: 1; width: 100%; display: flex; flex-direction: column-reverse;
  background: #181825; border-radius: 3px; overflow: hidden; min-height: 4px;
  max-height: 60px;
}
.bar-seg { width: 100%; min-height: 2px; }
.bar-seg--challenges { background: #a6e3a1; }
.bar-seg--quizzes { background: #89b4fa; }
.bar-seg--bonus { background: #f9e2af; }
.bar-label { font-size: 0.65rem; color: #6c7086; text-transform: capitalize; }

.bars-legend { display: flex; gap: 1rem; }
.legend-item { display: flex; align-items: center; gap: 0.3rem; font-size: 0.75rem; color: #6c7086; }
.legend-dot { width: 8px; height: 8px; border-radius: 2px; }
.legend-dot--challenges { background: #a6e3a1; }
.legend-dot--quizzes { background: #89b4fa; }
.legend-dot--bonus { background: #f9e2af; }

/* Tabla entregas */
.attempts-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
.attempts-table th {
  text-align: left; padding: 0.3rem 0.5rem;
  color: #6c7086; font-weight: 500; border-bottom: 1px solid #313244;
}
.attempts-table td { padding: 0.4rem 0.5rem; border-bottom: 1px solid #1e1e2e; color: #cdd6f4; }
.cell-title { max-width: 140px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.cell-center { text-align: center; }
.cell-pts { font-weight: 600; color: #a6e3a1; }
.cell-date { color: #6c7086; white-space: nowrap; }

.diff-chip {
  font-size: 0.7rem; font-weight: 700; padding: 0.1rem 0.35rem;
  border-radius: 4px;
}
.diff--easy { background: rgba(166,227,161,0.15); color: #a6e3a1; }
.diff--medium { background: rgba(249,226,175,0.15); color: #f9e2af; }
.diff--hard { background: rgba(243,139,168,0.15); color: #f38ba8; }

.bonus-tag { font-size: 0.7rem; color: #f9e2af; margin-left: 2px; }

.status-chip { font-size: 0.72rem; font-weight: 600; padding: 0.1rem 0.4rem; border-radius: 999px; }
.status--ok { background: rgba(166,227,161,0.15); color: #a6e3a1; }
.status--fail { background: rgba(243,139,168,0.15); color: #f38ba8; }
.status--pending { background: rgba(249,226,175,0.15); color: #f9e2af; }
</style>
