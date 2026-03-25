<template>
  <div class="ssp">
    <div v-if="loadingSnippets" class="ssp-loading"><span class="spinner" /> Cargando...</div>

    <div v-else-if="!snippets || !snippets.snippets.length" class="ssp-empty">
      El alumno no tiene snippets guardados.
    </div>

    <div v-else class="snippets-grid">
      <div v-for="s in snippets.snippets" :key="s.id" class="snippet-card">
        <div class="sc-header">
          <span class="sc-title">{{ s.title }}</span>
          <span class="sc-lang">{{ s.language }}</span>
        </div>
        <pre class="sc-preview">{{ s.code_preview }}</pre>
        <div class="sc-footer">
          <span v-for="tag in s.tags" :key="tag" class="sc-tag">{{ tag }}</span>
          <span class="sc-date">{{ fmtDate(s.updated_at) }}</span>
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
const { snippets, loadingSnippets } = storeToRefs(store)

onMounted(() => store.loadSnippets())

function fmtDate(iso: string) {
  return new Date(iso).toLocaleDateString('es-AR', { day: '2-digit', month: 'short', year: 'numeric' })
}
</script>

<style scoped>
.ssp { display: flex; flex-direction: column; }
.ssp-loading { display: flex; align-items: center; gap: 0.5rem; color: #6c7086; font-size: 0.85rem; padding: 1rem; }
.ssp-empty { font-size: 0.85rem; color: #6c7086; padding: 0.5rem 0; }

.snippets-grid {
  display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.75rem;
}

@media (max-width: 640px) {
  .snippets-grid { grid-template-columns: 1fr; }
}

.snippet-card {
  background: #181825; border: 1px solid #313244; border-radius: 8px;
  padding: 0.75rem; display: flex; flex-direction: column; gap: 0.5rem;
  overflow: hidden;
}

.sc-header {
  display: flex; align-items: center; justify-content: space-between; gap: 0.5rem;
}

.sc-title {
  font-size: 0.85rem; font-weight: 600; color: #cdd6f4;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

.sc-lang {
  font-size: 0.7rem; padding: 0.1rem 0.4rem; border-radius: 4px;
  background: rgba(203,166,247,0.15); color: #cba6f7; flex-shrink: 0;
}

.sc-preview {
  margin: 0; font-size: 0.75rem; font-family: 'JetBrains Mono', monospace;
  color: #a6adc8; background: #11111b; border-radius: 4px;
  padding: 0.5rem; white-space: pre-wrap; overflow: hidden;
  max-height: 60px;
}

.sc-footer {
  display: flex; align-items: center; gap: 0.4rem; flex-wrap: wrap;
}

.sc-tag {
  font-size: 0.68rem; padding: 0.1rem 0.35rem; border-radius: 999px;
  background: #313244; color: #6c7086;
}

.sc-date {
  font-size: 0.7rem; color: #45475a; margin-left: auto;
}
</style>
