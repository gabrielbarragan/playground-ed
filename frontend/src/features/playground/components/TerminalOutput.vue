<template>
  <div class="terminal-wrapper">
    <!-- Achievement toasts -->
    <div class="achievement-toasts">
      <transition-group name="toast">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          class="achievement-toast"
        >
          <span class="toast-icon">{{ toast.icon }}</span>
          <div class="toast-body">
            <span class="toast-title">¡Logro desbloqueado!</span>
            <span class="toast-name">{{ toast.name }}</span>
            <span class="toast-desc">{{ toast.description }}</span>
            <span v-if="toast.points_bonus > 0" class="toast-pts">+{{ toast.points_bonus }} pts</span>
          </div>
        </div>
      </transition-group>
    </div>

    <div class="terminal-pane-header">
      <span class="pane-label">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="4 17 10 11 4 5" />
          <line x1="12" y1="19" x2="20" y2="19" />
        </svg>
        Output
      </span>
      <span class="status-badge" :class="statusClass">{{ statusLabel }}</span>
    </div>
    <div ref="terminalRef" class="terminal-container" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { Terminal } from '@xterm/xterm'
import { FitAddon } from '@xterm/addon-fit'
import '@xterm/xterm/css/xterm.css'
import { usePlaygroundStore } from '@/stores/usePlaygroundStore'
import type { ExecutionStatus, WsServerMessage, AchievementData } from '@/types/playground'

// ── Props para el badge de estado ─────────────────────────
const props = defineProps<{ status: ExecutionStatus }>()

const statusLabel = computed(() => {
  const map: Record<ExecutionStatus, string> = {
    idle:        'Listo',
    running:     'Ejecutando...',
    success:     'OK',
    error:       'Error',
    timeout:     'Timeout',
    server_down: 'Sin servidor',
  }
  return map[props.status]
})

const statusClass = computed(() => ({
  'badge--idle':    props.status === 'idle',
  'badge--running': props.status === 'running',
  'badge--success': props.status === 'success',
  'badge--error':   props.status === 'error' || props.status === 'timeout',
  'badge--down':    props.status === 'server_down',
}))

// ── Achievement toasts ────────────────────────────────────
interface AchievementToast extends AchievementData { id: number }
const toasts = ref<AchievementToast[]>([])
let _toastId = 0

function showAchievementToast(data: AchievementData, delay = 0) {
  setTimeout(() => {
    const id = ++_toastId
    toasts.value.push({ ...data, id })
    setTimeout(() => {
      toasts.value = toasts.value.filter(t => t.id !== id)
    }, 4500)
  }, delay)
}

// ── Terminal setup ────────────────────────────────────────
const store = usePlaygroundStore()
const terminalRef = ref<HTMLDivElement | null>(null)
let terminal: Terminal | null = null
let fitAddon: FitAddon | null = null
let resizeObserver: ResizeObserver | null = null

// Buffer de línea para input interactivo
let inputBuffer = ''
let isAcceptingInput = false

const A = {
  reset:   '\x1b[0m',
  bold:    '\x1b[1m',
  dim:     '\x1b[2m',
  green:   '\x1b[32m',
  red:     '\x1b[31m',
  yellow:  '\x1b[33m',
  cyan:    '\x1b[36m',
  gray:    '\x1b[90m',
}

// ── Handlers de mensajes WebSocket ────────────────────────
function handleWsMessage(msg: WsServerMessage) {
  if (!terminal) return

  switch (msg.type) {
    case 'stdout':
      // Señal de reset (enviada por resetTerminal en el store)
      if (msg.data === '') {
        clearAndShowIdle()
        return
      }
      terminal.write(msg.data)
      break

    case 'stderr':
      terminal.write(`${A.red}${msg.data}${A.reset}`)
      break

    case 'exit':
      isAcceptingInput = false
      inputBuffer = ''
      terminal.writeln('')
      terminal.writeln(
        msg.return_code === 0
          ? `${A.green}${A.bold}✓ Proceso terminado (código 0)${A.reset}`
          : `${A.red}${A.bold}✗ Proceso terminado con error (código 1)${A.reset}`,
      )
      break

    case 'timeout':
      isAcceptingInput = false
      inputBuffer = ''
      terminal.writeln('')
      terminal.writeln(`${A.yellow}${A.bold}⏱ Tiempo máximo de ejecución alcanzado${A.reset}`)
      break

    case 'error':
      isAcceptingInput = false
      terminal.writeln(`${A.red}${msg.message}${A.reset}`)
      break

    case 'achievement':
      showAchievementToast(msg.data)
      break
  }
}

// ── Input interactivo del usuario ─────────────────────────
function setupInputHandler() {
  terminal?.onData((data: string) => {
    if (!isAcceptingInput) return

    if (data === '\r' || data === '\n') {
      // Enter: enviar línea al subprocess
      terminal!.write('\r\n')
      store.sendStdin(inputBuffer + '\n')
      inputBuffer = ''
    } else if (data === '\x7f' || data === '\x08') {
      // Backspace
      if (inputBuffer.length > 0) {
        inputBuffer = inputBuffer.slice(0, -1)
        terminal!.write('\b \b')
      }
    } else if (data === '\x03') {
      // Ctrl+C → kill
      terminal!.writeln('^C')
      store.stopExecution()
    } else if (data >= ' ' || data === '\t') {
      // Carácter imprimible
      inputBuffer += data
      terminal!.write(data)
    }
  })
}

// ── Estado visual del terminal ─────────────────────────────
function clearAndShowIdle() {
  terminal?.clear()
  terminal?.writeln(`${A.gray}Python Playground listo.${A.reset}`)
  terminal?.writeln(`${A.gray}Presiona ${A.reset}${A.cyan}Ctrl+Enter${A.reset}${A.gray} para ejecutar.${A.reset}`)
  isAcceptingInput = false
  inputBuffer = ''
}

function prepareForRun() {
  terminal?.clear()
  terminal?.writeln(`${A.cyan}${A.bold}>>> ${A.reset}${A.dim}main.py${A.reset}`)
  terminal?.writeln('')
  isAcceptingInput = true
  inputBuffer = ''
}

// ── Lifecycle ─────────────────────────────────────────────
onMounted(() => {
  if (!terminalRef.value) return

  terminal = new Terminal({
    theme: {
      background:       '#1e1e2e',
      foreground:       '#cdd6f4',
      cursor:           '#f5e0dc',
      cursorAccent:     '#1e1e2e',
      selectionBackground: '#45475a80',
      black:         '#45475a', brightBlack:   '#585b70',
      red:           '#f38ba8', brightRed:     '#f38ba8',
      green:         '#a6e3a1', brightGreen:   '#a6e3a1',
      yellow:        '#f9e2af', brightYellow:  '#f9e2af',
      blue:          '#89b4fa', brightBlue:    '#89b4fa',
      magenta:       '#cba6f7', brightMagenta: '#cba6f7',
      cyan:          '#89dceb', brightCyan:    '#89dceb',
      white:         '#bac2de', brightWhite:   '#cdd6f4',
    },
    fontFamily:   "'JetBrains Mono', 'Fira Code', monospace",
    fontSize:     13,
    lineHeight:   1.5,
    cursorBlink:  true,
    cursorStyle:  'block',
    convertEol:   true,
    scrollback:   2000,
    disableStdin: false,
  })

  fitAddon = new FitAddon()
  terminal.loadAddon(fitAddon)
  terminal.open(terminalRef.value)
  fitAddon.fit()

  setupInputHandler()
  clearAndShowIdle()

  // Registra el handler de mensajes en el store
  store.onWsMessage((msg) => {
    if (msg.type === 'stdout' && msg.data !== '' && isAcceptingInput === false) {
      // Primera salida → marcar que hay un proceso corriendo
      isAcceptingInput = true
    }
    handleWsMessage(msg)
  })

  // Cuando empieza una nueva ejecución, limpiar terminal
  let prevStatus = props.status
  const unwatch = setInterval(() => {
    if (props.status === 'running' && prevStatus !== 'running') {
      prepareForRun()
    }
    prevStatus = props.status
  }, 50)

  resizeObserver = new ResizeObserver(() => fitAddon?.fit())
  resizeObserver.observe(terminalRef.value)

  onBeforeUnmount(() => {
    clearInterval(unwatch)
    resizeObserver?.disconnect()
    terminal?.dispose()
  })
})
</script>

<style scoped>
.terminal-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  position: relative;
}

.terminal-pane-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #181825;
  border-bottom: 1px solid #313244;
  padding: 0 0.75rem;
  flex-shrink: 0;
  height: 36px;
}

.pane-label {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.75rem;
  color: #cdd6f4;
  user-select: none;
}

.pane-label svg { color: #89b4fa; }

.status-badge {
  font-size: 0.7rem;
  padding: 0.15rem 0.55rem;
  border-radius: 9999px;
  font-weight: 600;
  letter-spacing: 0.02em;
  transition: background 0.2s, color 0.2s;
}

.badge--idle    { background: #313244; color: #6c7086; }
.badge--running { background: #2a2a1e; color: #f9e2af; animation: pulse 1.2s ease-in-out infinite; }
.badge--success { background: #1e3a2f; color: #a6e3a1; }
.badge--error   { background: #3a1e1e; color: #f38ba8; }
.badge--down    { background: #3a2a1e; color: #fab387; }

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.5; }
}

.terminal-container {
  flex: 1;
  min-height: 0;
  padding: 0.5rem 0.25rem;
  background: #1e1e2e;
  overflow: hidden;
}

/* ── Achievement toasts ─────────────────────────────────── */
.achievement-toasts {
  position: absolute;
  bottom: 1rem;
  right: 1rem;
  z-index: 100;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  pointer-events: none;
}

.achievement-toast {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  background: #181825;
  border: 1px solid #cba6f7;
  border-radius: 10px;
  padding: 0.75rem 1rem;
  min-width: 240px;
  max-width: 300px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.5);
}

.toast-icon {
  font-size: 1.75rem;
  line-height: 1;
  flex-shrink: 0;
}

.toast-body {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.toast-title {
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #cba6f7;
}

.toast-name {
  font-size: 0.85rem;
  font-weight: 700;
  color: #cdd6f4;
}

.toast-desc {
  font-size: 0.75rem;
  color: #6c7086;
  line-height: 1.3;
}

.toast-pts {
  font-size: 0.75rem;
  font-weight: 700;
  color: #a6e3a1;
  margin-top: 0.1rem;
}

/* Transition */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.35s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(40px);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(40px);
}
</style>