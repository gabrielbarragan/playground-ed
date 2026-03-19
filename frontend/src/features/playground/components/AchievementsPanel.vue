<template>
  <Teleport to="body">
    <div class="panel-backdrop" @click.self="$emit('close')" />
    <aside class="panel">
      <div class="panel-header">
        <h2 class="panel-title">
          Logros
          <span v-if="data" class="panel-counter">{{ data.earned_count }} / {{ data.total }}</span>
        </h2>
        <button class="panel-close" @click="$emit('close')">✕</button>
      </div>

      <div v-if="loading" class="panel-state">
        <span class="spinner" />
        <span>Cargando...</span>
      </div>

      <template v-else-if="data">
        <!-- Earned -->
        <div v-if="data.earned.length" class="section">
          <h3 class="section-title">Desbloqueados</h3>
          <div class="ach-grid">
            <div
              v-for="ua in data.earned"
              :key="ua.id"
              class="ach-card ach-card--earned"
            >
              <span class="ach-icon">{{ ua.achievement.icon }}</span>
              <span class="ach-name">{{ ua.achievement.name }}</span>
              <span class="ach-desc">{{ ua.achievement.description }}</span>
              <span v-if="ua.achievement.points_bonus > 0" class="ach-pts">
                +{{ ua.achievement.points_bonus }} pts
              </span>
              <span class="ach-date">{{ formatDate(ua.earned_at) }}</span>
            </div>
          </div>
        </div>

        <!-- Locked -->
        <div v-if="data.locked.length" class="section">
          <h3 class="section-title">Por descubrir</h3>
          <div class="ach-grid">
            <div
              v-for="locked in data.locked"
              :key="locked.id"
              class="ach-card ach-card--locked"
            >
              <span class="ach-icon">❓</span>
              <span class="ach-name">???</span>
              <span class="ach-desc">Sigue explorando el código...</span>
            </div>
          </div>
        </div>

        <div v-if="!data.earned.length && !data.locked.length" class="panel-state panel-empty">
          <p>No hay logros configurados aún.</p>
        </div>
      </template>
    </aside>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { achievementsApi, type MyAchievementsResponse } from '@/api/achievementsApi'

defineEmits<{ close: [] }>()

const loading = ref(true)
const data = ref<MyAchievementsResponse | null>(null)

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('es-AR', { day: '2-digit', month: 'short', year: 'numeric' })
}

onMounted(async () => {
  try {
    data.value = await achievementsApi.myAchievements()
  } catch { /* ignore */ } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.panel-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 200;
}

.panel {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  width: 360px;
  background: #181825;
  border-left: 1px solid #313244;
  z-index: 201;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #313244;
  flex-shrink: 0;
}

.panel-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #cdd6f4;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.panel-counter {
  font-size: 0.7rem;
  background: #313244;
  color: #cba6f7;
  padding: 0.1rem 0.5rem;
  border-radius: 9999px;
  font-weight: 600;
}

.panel-close {
  background: none;
  border: none;
  color: #6c7086;
  font-size: 0.9rem;
  cursor: pointer;
  padding: 0.25rem;
  transition: color 0.15s;
}

.panel-close:hover { color: #cdd6f4; }

.panel-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 0.5rem;
  color: #6c7086;
  font-size: 0.85rem;
}

.panel-empty { text-align: center; }

.section {
  padding: 0.75rem 1rem 0;
  overflow-y: auto;
}

.section + .section { padding-top: 0.5rem; }

.section-title {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #6c7086;
  margin-bottom: 0.5rem;
}

.ach-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
  padding-bottom: 0.75rem;
}

.ach-card {
  background: #1e1e2e;
  border: 1px solid #313244;
  border-radius: 8px;
  padding: 0.6rem 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.ach-card--earned {
  border-color: #45475a;
}

.ach-card--locked {
  opacity: 0.45;
}

.ach-icon {
  font-size: 1.5rem;
  line-height: 1;
}

.ach-name {
  font-size: 0.8rem;
  font-weight: 700;
  color: #cdd6f4;
  line-height: 1.2;
}

.ach-desc {
  font-size: 0.7rem;
  color: #6c7086;
  line-height: 1.3;
}

.ach-pts {
  font-size: 0.7rem;
  font-weight: 700;
  color: #a6e3a1;
}

.ach-date {
  font-size: 0.65rem;
  color: #45475a;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #313244;
  border-top-color: #cba6f7;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }
</style>