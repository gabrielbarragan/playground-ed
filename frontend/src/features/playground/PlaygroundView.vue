<template>
  <div
    class="playground-layout"
    :class="{ 'is-dragging': isDragging }"
    @keydown.ctrl.enter.prevent="handleRun"
    @keydown.meta.enter.prevent="handleRun"
  >
    <!-- Header -->
    <header class="playground-header">
      <div class="header-left">
        <svg class="logo-icon" width="20" height="20" viewBox="0 0 24 24" fill="none">
          <path
            d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14H9V8h2v8zm4 0h-2V8h2v8z"
            fill="#cba6f7"
          />
        </svg>
        <span class="header-title">FANAMA Python Playground</span>
        <span v-if="store.serverVersion" class="header-version">{{ store.serverVersion }}</span>
      </div>

      <div class="header-right">
        <span class="shortcut-hint">
          <kbd>Ctrl</kbd><span>+</span><kbd>Enter</kbd> para ejecutar
        </span>
        <div class="health-dot-wrapper">
          <span class="health-dot" :class="store.serverHealth ? 'dot--ok' : 'dot--down'" />
          <span class="health-label" :class="store.serverHealth ? 'label--ok' : 'label--down'">
            {{ store.serverHealth ? 'Servidor OK' : 'Desconectado' }}
          </span>
        </div>
      </div>
    </header>

    <!-- Body -->
    <main ref="bodyRef" class="playground-body">
      <!-- Editor pane -->
      <section class="pane" :style="editorPaneStyle">
        <MonacoEditor v-model="store.code" @run="handleRun" />
        <div class="editor-toolbar">
          <button
            class="btn-run"
            :class="{ 'btn-run--loading': store.status === 'running' }"
            :disabled="store.status === 'running' || !store.serverHealth"
            @click="handleRun"
          >
            <span v-if="store.status !== 'running'" class="btn-run__content">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor">
                <polygon points="5 3 19 12 5 21 5 3" />
              </svg>
              Ejecutar
            </span>
            <span v-else class="btn-run__content">
              <span class="spinner" />
              Ejecutando...
            </span>
          </button>

          <button
            v-if="store.status === 'running'"
            class="btn-stop"
            @click="store.stopExecution()"
          >
            <svg width="11" height="11" viewBox="0 0 24 24" fill="currentColor">
              <rect x="3" y="3" width="18" height="18" rx="2" />
            </svg>
            Detener
          </button>

          <button v-else class="btn-secondary" @click="store.resetTerminal()">
            Limpiar
          </button>

          <span v-if="!store.serverHealth" class="toolbar-warning">
            El servidor no está disponible
          </span>
        </div>
      </section>

      <!-- Resizable divider -->
      <div
        class="pane-divider"
        :class="{ 'pane-divider--dragging': isDragging }"
        @mousedown.prevent="startDrag"
        @touchstart.prevent="startDragTouch"
        @dblclick="resetSize"
      >
        <div class="divider-handle">
          <span class="divider-dot" />
          <span class="divider-dot" />
          <span class="divider-dot" />
        </div>
      </div>

      <!-- Output pane -->
      <section class="pane" :style="outputPaneStyle">
        <TerminalOutput :status="store.status" />
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { usePlaygroundStore } from '@/stores/usePlaygroundStore'
import MonacoEditor from './components/MonacoEditor.vue'
import TerminalOutput from './components/TerminalOutput.vue'

const store = usePlaygroundStore()

// ── Resize logic ──────────────────────────────────────────
const bodyRef = ref<HTMLElement | null>(null)
const isDragging = ref(false)
const isMobile = ref(false)

// Tamaño del panel del editor en porcentaje (20–80)
const editorSize = ref(50)

const MIN_SIZE = 20
const MAX_SIZE = 80

const editorPaneStyle = computed(() =>
  isMobile.value
    ? { height: `${editorSize.value}%`, width: '100%' }
    : { width: `${editorSize.value}%`, height: '100%' },
)

const outputPaneStyle = computed(() =>
  isMobile.value
    ? { height: `${100 - editorSize.value}%`, width: '100%' }
    : { width: `${100 - editorSize.value}%`, height: '100%' },
)

function clamp(value: number): number {
  return Math.min(MAX_SIZE, Math.max(MIN_SIZE, value))
}

function startDrag(e: MouseEvent) {
  isDragging.value = true
  const startPos = isMobile.value ? e.clientY : e.clientX
  const startSize = editorSize.value

  function onMove(e: MouseEvent) {
    if (!bodyRef.value) return
    const rect = bodyRef.value.getBoundingClientRect()
    const totalSize = isMobile.value ? rect.height : rect.width
    const delta = (isMobile.value ? e.clientY : e.clientX) - startPos
    editorSize.value = clamp(startSize + (delta / totalSize) * 100)
  }

  function onUp() {
    isDragging.value = false
    document.removeEventListener('mousemove', onMove)
    document.removeEventListener('mouseup', onUp)
  }

  document.addEventListener('mousemove', onMove)
  document.addEventListener('mouseup', onUp)
}

function startDragTouch(e: TouchEvent) {
  isDragging.value = true
  const touch = e.touches[0]!
  const startPos = isMobile.value ? touch.clientY : touch.clientX
  const startSize = editorSize.value

  function onMove(e: TouchEvent) {
    if (!bodyRef.value) return
    const t = e.touches[0]!
    const rect = bodyRef.value.getBoundingClientRect()
    const totalSize = isMobile.value ? rect.height : rect.width
    const delta = (isMobile.value ? t.clientY : t.clientX) - startPos
    editorSize.value = clamp(startSize + (delta / totalSize) * 100)
  }

  function onEnd() {
    isDragging.value = false
    document.removeEventListener('touchmove', onMove)
    document.removeEventListener('touchend', onEnd)
  }

  document.addEventListener('touchmove', onMove, { passive: true })
  document.addEventListener('touchend', onEnd)
}

function resetSize() {
  editorSize.value = 50
}

// ── Mobile detection ──────────────────────────────────────
function checkMobile() {
  isMobile.value = window.innerWidth <= 768
}

// ── Playground logic ──────────────────────────────────────
function handleRun() {
  if (store.status === 'running' || !store.serverHealth) return
  store.executeCode()
}

onMounted(async () => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
  await Promise.all([store.checkHealth(), store.fetchVersion()])
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped>
/* ── Layout ──────────────────────────────────────────────── */
.playground-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
  outline: none;
}

/* Bloquea selección de texto en toda la app mientras se arrastra */
.is-dragging {
  user-select: none;
}

.is-dragging * {
  pointer-events: none;
}

.is-dragging .pane-divider {
  pointer-events: all;
}

/* ── Header ──────────────────────────────────────────────── */
.playground-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1rem;
  height: 48px;
  background: #181825;
  border-bottom: 1px solid #313244;
  flex-shrink: 0;
  gap: 1rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.logo-icon { flex-shrink: 0; }

.header-title {
  font-weight: 700;
  font-size: 0.9rem;
  color: #cdd6f4;
  white-space: nowrap;
}

.header-version {
  font-size: 0.7rem;
  color: #45475a;
  background: #313244;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.shortcut-hint {
  display: flex;
  align-items: center;
  gap: 0.2rem;
  font-size: 0.72rem;
  color: #6c7086;
}

.shortcut-hint kbd {
  display: inline-flex;
  align-items: center;
  padding: 0.1rem 0.35rem;
  background: #313244;
  border: 1px solid #45475a;
  border-radius: 3px;
  font-family: inherit;
  font-size: 0.68rem;
  color: #a6adc8;
  line-height: 1.4;
}

.health-dot-wrapper {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.health-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}

.dot--ok  { background: #a6e3a1; box-shadow: 0 0 6px #a6e3a180; }
.dot--down { background: #f38ba8; box-shadow: 0 0 6px #f38ba880; }

.health-label { font-size: 0.75rem; }
.label--ok   { color: #a6e3a1; }
.label--down { color: #f38ba8; }

/* ── Body ────────────────────────────────────────────────── */
.playground-body {
  display: flex;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.pane {
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 0;
  overflow: hidden;
  flex-shrink: 0;
}

/* ── Divider ─────────────────────────────────────────────── */
.pane-divider {
  position: relative;
  width: 5px;
  flex-shrink: 0;
  background: #313244;
  cursor: col-resize;
  transition: background 0.15s;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pane-divider:hover,
.pane-divider--dragging {
  background: #585b70;
}

.pane-divider--dragging {
  background: #cba6f7;
}

/* Área de clic extendida sin agrandar visualmente */
.pane-divider::before {
  content: '';
  position: absolute;
  inset: 0 -4px;
}

.divider-handle {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  opacity: 0;
  transition: opacity 0.15s;
}

.pane-divider:hover .divider-handle,
.pane-divider--dragging .divider-handle {
  opacity: 1;
}

.divider-dot {
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: #cdd6f4;
}

/* ── Toolbar ─────────────────────────────────────────────── */
.editor-toolbar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: #181825;
  border-top: 1px solid #313244;
  flex-shrink: 0;
}

.btn-run {
  display: inline-flex;
  align-items: center;
  padding: 0.42rem 1.1rem;
  background: #cba6f7;
  color: #1e1e2e;
  border: none;
  border-radius: 6px;
  font-weight: 700;
  font-size: 0.82rem;
  font-family: inherit;
  cursor: pointer;
  transition: background 0.15s, transform 0.1s;
  user-select: none;
}

.btn-run:hover:not(:disabled) {
  background: #d4b4ff;
  transform: translateY(-1px);
}

.btn-run:active:not(:disabled) {
  transform: translateY(0);
}

.btn-run:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none;
}

.btn-run--loading {
  background: #45475a;
  color: #cdd6f4;
}

.btn-run__content {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.spinner {
  width: 11px;
  height: 11px;
  border: 2px solid #6c7086;
  border-top-color: #cdd6f4;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.btn-secondary {
  padding: 0.42rem 0.8rem;
  background: transparent;
  color: #6c7086;
  border: 1px solid #313244;
  border-radius: 6px;
  font-size: 0.82rem;
  font-family: inherit;
  cursor: pointer;
  transition: border-color 0.15s, color 0.15s;
  user-select: none;
}

.btn-secondary:hover:not(:disabled) {
  border-color: #585b70;
  color: #a6adc8;
}

.btn-secondary:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-stop {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.42rem 0.9rem;
  background: #3a1e1e;
  color: #f38ba8;
  border: 1px solid #f38ba840;
  border-radius: 6px;
  font-size: 0.82rem;
  font-family: inherit;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
  user-select: none;
}

.btn-stop:hover {
  background: #4a2020;
  border-color: #f38ba880;
}

.toolbar-warning {
  margin-left: auto;
  font-size: 0.72rem;
  color: #f38ba8;
}

/* ── Responsive ──────────────────────────────────────────── */
@media (max-width: 768px) {
  .playground-body {
    flex-direction: column;
  }

  .pane-divider {
    width: 100%;
    height: 5px;
    cursor: row-resize;
  }

  .pane-divider::before {
    inset: -4px 0;
  }

  .divider-handle {
    flex-direction: row;
  }

  .shortcut-hint {
    display: none;
  }
}
</style>