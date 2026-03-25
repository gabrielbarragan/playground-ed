<template>
  <Teleport to="body">
    <Transition name="drawer-fade">
      <div v-if="userId" class="drawer-overlay" @click.self="store.close()">
        <div class="drawer">
          <!-- Header del drawer -->
          <div class="drawer-header">
            <span class="drawer-heading">Perfil del alumno</span>
            <button class="drawer-close" @click="store.close()">✕</button>
          </div>

          <!-- Loading inicial -->
          <div v-if="loadingSummary" class="drawer-loading">
            <span class="big-spinner" />
            <span>Cargando perfil...</span>
          </div>

          <div v-else-if="summary" class="drawer-body">
            <!-- Header con stats -->
            <StudentProfileHeader
              :summary="summary"
              @go-to-submissions="$emit('go-to-submissions')"
            />

            <!-- Tabs -->
            <div class="drawer-tabs">
              <button
                v-for="tab in TABS"
                :key="tab.id"
                class="drawer-tab"
                :class="{ 'drawer-tab--active': activeTab === tab.id }"
                @click="activeTab = tab.id"
              >{{ tab.label }}</button>
            </div>

            <!-- Contenido por tab -->
            <div class="drawer-tab-content">
              <StudentActivityPanel v-if="activeTab === 'activity'" :summary="summary" />
              <StudentChallengesPanel v-if="activeTab === 'challenges'" />
              <StudentQuizzesPanel v-if="activeTab === 'quizzes'" />
              <StudentSnippetsPanel v-if="activeTab === 'snippets'" />
              <StudentAchievementsPanel v-if="activeTab === 'achievements'" />
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useStudentProfileStore } from '@/stores/useStudentProfileStore'
import StudentProfileHeader from './StudentProfileHeader.vue'
import StudentActivityPanel from './StudentActivityPanel.vue'
import StudentChallengesPanel from './StudentChallengesPanel.vue'
import StudentQuizzesPanel from './StudentQuizzesPanel.vue'
import StudentSnippetsPanel from './StudentSnippetsPanel.vue'
import StudentAchievementsPanel from './StudentAchievementsPanel.vue'

defineEmits(['go-to-submissions'])

const store = useStudentProfileStore()
const { userId, summary, loadingSummary } = storeToRefs(store)

const activeTab = ref('activity')

const TABS = [
  { id: 'activity', label: 'Actividad' },
  { id: 'challenges', label: 'Retos' },
  { id: 'quizzes', label: 'Quizzes' },
  { id: 'snippets', label: 'Snippets' },
  { id: 'achievements', label: 'Logros' },
]

// Resetear tab al cambiar de alumno
watch(userId, () => { activeTab.value = 'activity' })
</script>

<style scoped>
.drawer-overlay {
  position: fixed; inset: 0; z-index: 200;
  background: rgba(0, 0, 0, 0.5);
  display: flex; justify-content: flex-end;
}

.drawer {
  width: min(620px, 95vw); height: 100vh;
  background: #1e1e2e; border-left: 1px solid #313244;
  display: flex; flex-direction: column; overflow: hidden;
}

.drawer-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 1rem 1.25rem; border-bottom: 1px solid #313244;
  flex-shrink: 0;
}

.drawer-heading {
  font-size: 0.9rem; font-weight: 600; color: #a6adc8;
  text-transform: uppercase; letter-spacing: 0.05em;
}

.drawer-close {
  background: none; border: none; color: #6c7086;
  font-size: 1rem; cursor: pointer; padding: 0.25rem 0.5rem;
  border-radius: 4px; line-height: 1;
}
.drawer-close:hover { color: #cdd6f4; background: #313244; }

.drawer-loading {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 1rem; color: #6c7086;
}

.drawer-body {
  flex: 1; display: flex; flex-direction: column; overflow: hidden;
}

.drawer-body > :first-child {
  padding: 1.25rem; border-bottom: 1px solid #313244; flex-shrink: 0;
}

.drawer-tabs {
  display: flex; gap: 0.25rem; padding: 0.6rem 1.25rem;
  border-bottom: 1px solid #313244; flex-shrink: 0; overflow-x: auto;
}

.drawer-tab {
  background: none; border: none; color: #6c7086;
  font-size: 0.85rem; cursor: pointer; padding: 0.3rem 0.75rem;
  border-radius: 6px; white-space: nowrap; flex-shrink: 0;
}
.drawer-tab:hover { color: #cdd6f4; background: #313244; }
.drawer-tab--active { color: #cba6f7; background: rgba(203,166,247,0.1); }

.drawer-tab-content {
  flex: 1; overflow-y: auto; padding: 1.25rem;
}

/* Transición */
.drawer-fade-enter-active,
.drawer-fade-leave-active {
  transition: opacity 0.2s ease;
}
.drawer-fade-enter-active .drawer,
.drawer-fade-leave-active .drawer {
  transition: transform 0.25s ease;
}
.drawer-fade-enter-from { opacity: 0; }
.drawer-fade-enter-from .drawer { transform: translateX(40px); }
.drawer-fade-leave-to { opacity: 0; }
.drawer-fade-leave-to .drawer { transform: translateX(40px); }

/* Spinner global */
.big-spinner {
  width: 32px; height: 32px; border-radius: 50%;
  border: 3px solid #313244; border-top-color: #cba6f7;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
