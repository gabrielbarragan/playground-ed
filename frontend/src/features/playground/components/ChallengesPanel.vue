<template>
  <div class="challenges-panel">
    <div class="cp-header">
      <span class="cp-title">Retos</span>
      <button class="cp-close" @click="$emit('close')" title="Cerrar">✕</button>
    </div>

    <!-- Summary stats -->
    <div v-if="progress.length" class="cp-stats">
      <span class="cp-stat">
        <span class="cp-stat-val">{{ solvedCount }}</span>
        <span class="cp-stat-lbl">resueltos</span>
      </span>
      <span class="cp-stat-sep">·</span>
      <span class="cp-stat">
        <span class="cp-stat-val">{{ pendingCount }}</span>
        <span class="cp-stat-lbl">en revisión</span>
      </span>
      <span class="cp-stat-sep">·</span>
      <span class="cp-stat">
        <span class="cp-stat-val">{{ totalCount }}</span>
        <span class="cp-stat-lbl">total</span>
      </span>
    </div>

    <div v-if="store.loading" class="cp-loading">
      <span class="cp-spinner" /> Cargando retos...
    </div>

    <div v-else-if="!progress.length" class="cp-empty">
      No hay retos disponibles aún.
    </div>

    <div v-else class="cp-list">
      <!-- Group by difficulty -->
      <template v-for="diff in DIFFICULTIES" :key="diff.key">
        <div v-if="byDiff(diff.key).length" class="cp-group">
          <div class="cp-group-header">
            <span class="diff-dot" :class="`diff-dot--${diff.key}`" />
            <span class="cp-group-label">{{ diff.label }}</span>
            <span class="cp-group-count">{{ byDiff(diff.key).length }}</span>
          </div>
          <div
            v-for="c in byDiff(diff.key)" :key="c.id"
            class="cp-item"
            :class="[statusClass(c.status), { 'cp-item--active': activeId === c.id }]"
            @click="select(c)"
          >
            <div class="cp-item-left">
              <span class="cp-item-status-icon">{{ statusIcon(c.status) }}</span>
              <span class="cp-item-title">{{ c.title }}</span>
            </div>
            <div class="cp-item-right">
              <span class="cp-item-pts">{{ c.points }}p</span>
              <span v-for="course in c.courses" :key="course.id" class="cp-course-badge">{{ course.code }}</span>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useChallengesStore } from '@/stores/useChallengesStore'
import type { ChallengeProgress } from '@/types/challenges'

const emit = defineEmits<{
  close: []
  select: [id: string]
}>()

const props = defineProps<{ activeId: string | null }>()

const store = useChallengesStore()
const progress = computed(() => store.progress)

const DIFFICULTIES = [
  { key: 'easy',   label: 'Fácil' },
  { key: 'medium', label: 'Media' },
  { key: 'hard',   label: 'Difícil' },
]

const solvedCount  = computed(() => progress.value.filter(c => c.status === 'passed').length)
const pendingCount = computed(() => progress.value.filter(c => c.status === 'pending_review').length)
const totalCount   = computed(() => progress.value.length)

function byDiff(diff: string) {
  return progress.value.filter(c => c.difficulty === diff)
}

function statusIcon(status: string) {
  if (status === 'passed') return '✓'
  if (status === 'pending_review') return '⏳'
  return '○'
}

function statusClass(status: string) {
  if (status === 'passed') return 'cp-item--passed'
  if (status === 'pending_review') return 'cp-item--pending'
  return ''
}

function select(c: ChallengeProgress) {
  emit('select', c.id)
}

onMounted(() => {
  if (!progress.value.length) store.fetchProgress()
})
</script>

<style scoped>
.challenges-panel {
  width: 280px;
  min-width: 280px;
  background: #181825;
  border-right: 1px solid #313244;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.cp-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #313244;
  flex-shrink: 0;
}

.cp-title {
  font-size: 0.85rem;
  font-weight: 700;
  color: #cdd6f4;
  font-family: 'JetBrains Mono', monospace;
}

.cp-close {
  background: transparent;
  border: none;
  color: #45475a;
  font-size: 0.9rem;
  cursor: pointer;
  padding: 0.1rem 0.3rem;
  border-radius: 4px;
  line-height: 1;
  transition: color 0.15s;
}
.cp-close:hover { color: #cdd6f4; }

.cp-stats {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-bottom: 1px solid #313244;
  flex-shrink: 0;
}

.cp-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.05rem;
}

.cp-stat-val {
  font-size: 0.95rem;
  font-weight: 700;
  color: #cdd6f4;
  line-height: 1;
  font-family: 'JetBrains Mono', monospace;
}

.cp-stat-lbl {
  font-size: 0.6rem;
  color: #6c7086;
  font-family: 'JetBrains Mono', monospace;
}

.cp-stat-sep {
  color: #313244;
  font-size: 1rem;
  align-self: center;
}

.cp-loading, .cp-empty {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  color: #6c7086;
  font-size: 0.8rem;
  padding: 2rem 1rem;
  justify-content: center;
  font-family: 'JetBrains Mono', monospace;
}

.cp-spinner {
  display: inline-block;
  width: 13px;
  height: 13px;
  border: 2px solid #313244;
  border-top-color: #cba6f7;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
}
@keyframes spin { to { transform: rotate(360deg); } }

.cp-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem 0;
}

.cp-list::-webkit-scrollbar { width: 4px; }
.cp-list::-webkit-scrollbar-track { background: transparent; }
.cp-list::-webkit-scrollbar-thumb { background: #313244; border-radius: 2px; }

.cp-group { margin-bottom: 0.5rem; }

.cp-group-header {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.4rem 1rem 0.25rem;
}

.diff-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}
.diff-dot--easy   { background: #a6e3a1; }
.diff-dot--medium { background: #fab387; }
.diff-dot--hard   { background: #f38ba8; }

.cp-group-label {
  font-size: 0.68rem;
  font-weight: 700;
  color: #6c7086;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  font-family: 'JetBrains Mono', monospace;
}

.cp-group-count {
  font-size: 0.65rem;
  color: #45475a;
  margin-left: 0.25rem;
  font-family: 'JetBrains Mono', monospace;
}

.cp-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 1rem;
  cursor: pointer;
  gap: 0.5rem;
  transition: background 0.1s;
  border-left: 2px solid transparent;
}

.cp-item:hover { background: #1e1e2e; }

.cp-item--active {
  background: #1e1e2e;
  border-left-color: #cba6f7;
}

.cp-item-left {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 0;
}

.cp-item-status-icon {
  font-size: 0.7rem;
  color: #45475a;
  flex-shrink: 0;
  width: 14px;
  text-align: center;
}

.cp-item--passed .cp-item-status-icon { color: #a6e3a1; }
.cp-item--pending .cp-item-status-icon { color: #fab387; }

.cp-item-title {
  font-size: 0.8rem;
  color: #a6adc8;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-family: 'JetBrains Mono', monospace;
}

.cp-item--passed .cp-item-title { color: #a6e3a180; }
.cp-item--active .cp-item-title { color: #cdd6f4; }

.cp-item-right {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  flex-shrink: 0;
}

.cp-item-pts {
  font-size: 0.65rem;
  color: #45475a;
  font-family: 'JetBrains Mono', monospace;
}

.cp-course-badge {
  font-size: 0.6rem;
  padding: 0.08rem 0.35rem;
  border-radius: 3px;
  background: #313244;
  color: #cba6f7;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
}
</style>