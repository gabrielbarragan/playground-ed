<template>
  <div class="sacp">
    <div v-if="loadingAchievements" class="sacp-loading"><span class="spinner" /> Cargando...</div>

    <div v-else-if="!achievements || !achievements.achievements.length" class="sacp-empty">
      El alumno aún no ha desbloqueado logros en el Sandbox.
    </div>

    <div v-else class="achievements-list">
      <div v-for="a in achievements.achievements" :key="a.id" class="ach-item">
        <span class="ach-icon">{{ a.icon }}</span>
        <div class="ach-info">
          <span class="ach-name">{{ a.name }}</span>
          <span class="ach-desc">{{ a.description }}</span>
        </div>
        <div class="ach-right">
          <span v-if="a.points_bonus" class="ach-pts">+{{ a.points_bonus }} pts</span>
          <span class="ach-date">{{ fmtDate(a.earned_at) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useStudentProfileStore } from '@/stores/useStudentProfileStore'
import { storeToRefs } from 'pinia'

const store = useStudentProfileStore()
const { achievements, loadingAchievements } = storeToRefs(store)

onMounted(() => store.loadAchievements())

function fmtDate(iso: string) {
  return new Date(iso).toLocaleDateString('es-AR', { day: '2-digit', month: 'short', year: 'numeric' })
}
</script>

<style scoped>
.sacp { display: flex; flex-direction: column; }
.sacp-loading { display: flex; align-items: center; gap: 0.5rem; color: #6c7086; font-size: 0.85rem; padding: 1rem; }
.sacp-empty { font-size: 0.85rem; color: #6c7086; padding: 0.5rem 0; }

.achievements-list { display: flex; flex-direction: column; gap: 0.5rem; }

.ach-item {
  display: flex; align-items: center; gap: 0.75rem;
  padding: 0.6rem 0.75rem; border-radius: 8px;
  background: #181825; border: 1px solid #313244;
}

.ach-icon { font-size: 1.4rem; flex-shrink: 0; }

.ach-info {
  display: flex; flex-direction: column; gap: 0.1rem; flex: 1; min-width: 0;
}

.ach-name { font-size: 0.85rem; font-weight: 600; color: #cdd6f4; }

.ach-desc { font-size: 0.75rem; color: #6c7086; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.ach-right {
  display: flex; flex-direction: column; align-items: flex-end; gap: 0.15rem; flex-shrink: 0;
}

.ach-pts {
  font-size: 0.75rem; font-weight: 700; color: #f9e2af;
}

.ach-date {
  font-size: 0.7rem; color: #45475a; white-space: nowrap;
}
</style>
