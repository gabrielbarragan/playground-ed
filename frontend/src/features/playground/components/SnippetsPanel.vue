<template>
  <Teleport to="body">
    <div class="panel-backdrop" @click.self="$emit('close')" />
    <aside class="panel">
      <div class="panel-header">
        <h2 class="panel-title">Mis Snippets</h2>
        <button class="panel-close" @click="$emit('close')">✕</button>
      </div>

      <div v-if="store.loading" class="panel-state">
        <span class="spinner" />
        <span>Cargando...</span>
      </div>

      <div v-else-if="store.snippets.length === 0" class="panel-state panel-empty">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z" stroke="#45475a" stroke-width="1.5" stroke-linejoin="round"/>
          <polyline points="14 2 14 8 20 8" stroke="#45475a" stroke-width="1.5" stroke-linejoin="round"/>
        </svg>
        <p>No tenés snippets guardados.</p>
        <p class="panel-empty-hint">Guardá tu código con el botón <strong>Guardar</strong>.</p>
      </div>

      <ul v-else class="snippet-list">
        <li
          v-for="snippet in store.snippets"
          :key="snippet.id"
          class="snippet-item"
          :class="{ 'snippet-item--active': store.activeSnippet?.id === snippet.id }"
        >
          <div class="snippet-info" @click="handleLoad(snippet)">
            <span class="snippet-title">{{ snippet.title }}</span>
            <div class="snippet-meta">
              <span v-if="snippet.tags.length" class="snippet-tags">
                <span v-for="tag in snippet.tags" :key="tag" class="tag">{{ tag }}</span>
              </span>
              <span class="snippet-date">{{ formatDate(snippet.updated_at) }}</span>
            </div>
          </div>
          <button
            class="snippet-delete"
            title="Eliminar"
            @click.stop="handleDelete(snippet.id)"
          >
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none">
              <polyline points="3 6 5 6 21 6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <path d="M19 6l-1 14H6L5 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M10 11v6M14 11v6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <path d="M9 6V4h6v2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </li>
      </ul>
    </aside>
  </Teleport>
</template>

<script setup lang="ts">
import { useSnippetsStore } from '@/stores/useSnippetsStore'
import type { Snippet } from '@/types/snippets'

const emit = defineEmits<{ close: []; load: [code: string] }>()
const store = useSnippetsStore()

function handleLoad(snippet: Snippet) {
  const code = store.load(snippet)
  emit('load', code)
  emit('close')
}

async function handleDelete(id: string) {
  await store.remove(id)
}

function formatDate(iso: string): string {
  const d = new Date(iso)
  return d.toLocaleDateString('es-AR', { day: '2-digit', month: 'short', year: 'numeric' })
}
</script>

<style scoped>
.panel-backdrop {
  position: fixed;
  inset: 0;
  background: #00000060;
  z-index: 90;
}

.panel {
  position: fixed;
  top: 0;
  right: 0;
  height: 100vh;
  width: 320px;
  background: #181825;
  border-left: 1px solid #313244;
  z-index: 91;
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
  font-size: 0.9rem;
  font-weight: 700;
  color: #cdd6f4;
}

.panel-close {
  background: transparent;
  border: none;
  color: #6c7086;
  font-size: 0.85rem;
  cursor: pointer;
  transition: color 0.15s;
}

.panel-close:hover { color: #cdd6f4; }

.panel-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
  flex: 1;
  color: #6c7086;
  font-size: 0.82rem;
}

.panel-empty {
  padding: 2rem 1.5rem;
  text-align: center;
}

.panel-empty-hint {
  color: #45475a;
  font-size: 0.78rem;
}

.panel-empty-hint strong { color: #6c7086; }

.snippet-list {
  list-style: none;
  overflow-y: auto;
  flex: 1;
  padding: 0.5rem 0;
}

.snippet-item {
  display: flex;
  align-items: stretch;
  border-bottom: 1px solid #1e1e2e;
  transition: background 0.12s;
}

.snippet-item:hover { background: #1e1e2e; }

.snippet-item--active { background: #1e1e2e; border-left: 2px solid #cba6f7; }

.snippet-info {
  flex: 1;
  padding: 0.75rem 1rem;
  cursor: pointer;
  min-width: 0;
}

.snippet-title {
  display: block;
  font-size: 0.85rem;
  color: #cdd6f4;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.snippet-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.3rem;
  flex-wrap: wrap;
}

.snippet-tags {
  display: flex;
  gap: 0.3rem;
  flex-wrap: wrap;
}

.tag {
  font-size: 0.68rem;
  background: #313244;
  color: #a6adc8;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
}

.snippet-date {
  font-size: 0.7rem;
  color: #45475a;
  margin-left: auto;
  white-space: nowrap;
}

.snippet-delete {
  background: transparent;
  border: none;
  color: #45475a;
  padding: 0 0.75rem;
  cursor: pointer;
  transition: color 0.15s;
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

.snippet-delete:hover { color: #f38ba8; }

.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid #313244;
  border-top-color: #cba6f7;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 480px) {
  .panel { width: 100vw; }
}
</style>