import { defineStore } from 'pinia'
import { ref, shallowRef } from 'vue'
import { metaApi } from '@/api/metaApi'
import { useAuthStore } from '@/stores/useAuthStore'
import type { ExecutionStatus, WsServerMessage } from '@/types/playground'

export const usePlaygroundStore = defineStore('playground', () => {
  // ── State ────────────────────────────────────────────────
  const code          = ref<string>('print("Hola, Playground!")\n')
  const status        = ref<ExecutionStatus>('idle')
  const serverHealth  = ref<boolean>(false)
  const serverVersion = ref<string | null>(null)

  // WebSocket actual. shallowRef para no hacer reactive el objeto WS completo.
  const ws = shallowRef<WebSocket | null>(null)

  // Callback registrado por TerminalOutput para recibir mensajes de streaming
  let _onMessage: ((msg: WsServerMessage) => void) | null = null

  // ── WebSocket helpers ─────────────────────────────────────
  function _wsUrl(): string {
    const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const base = `${proto}//${window.location.host}/ws/run`
    const token = useAuthStore().token
    return token ? `${base}?token=${token}` : base
  }

  function _teardown() {
    if (ws.value) {
      ws.value.onopen    = null
      ws.value.onmessage = null
      ws.value.onerror   = null
      ws.value.onclose   = null
      if (ws.value.readyState === WebSocket.OPEN) ws.value.close()
      ws.value = null
    }
  }

  // ── Actions ──────────────────────────────────────────────

  /** Registra el callback de TerminalOutput para recibir mensajes en streaming. */
  function onWsMessage(cb: (msg: WsServerMessage) => void) {
    _onMessage = cb
  }

  function executeCode() {
    if (status.value === 'running') return
    _teardown()

    const socket = new WebSocket(_wsUrl())
    ws.value = socket
    status.value = 'running'

    socket.onopen = () => {
      socket.send(JSON.stringify({ type: 'run', code: code.value }))
    }

    socket.onmessage = (event: MessageEvent) => {
      const msg: WsServerMessage = JSON.parse(event.data as string)

      // Actualiza el estado de alto nivel
      if (msg.type === 'exit') {
        status.value = msg.return_code === 0 ? 'success' : 'error'
      } else if (msg.type === 'timeout') {
        status.value = 'timeout'
      } else if (msg.type === 'error') {
        status.value = 'error'
      }

      // Delega el rendering al terminal
      _onMessage?.(msg)
    }

    socket.onerror = () => {
      status.value = 'server_down'
      serverHealth.value = false
      ws.value = null
    }

    socket.onclose = () => {
      if (status.value === 'running') status.value = 'idle'
      ws.value = null
    }
  }

  function sendStdin(data: string) {
    if (ws.value?.readyState === WebSocket.OPEN) {
      ws.value.send(JSON.stringify({ type: 'stdin', data }))
    }
  }

  function stopExecution() {
    if (ws.value?.readyState === WebSocket.OPEN) {
      ws.value.send(JSON.stringify({ type: 'kill' }))
    }
    status.value = 'idle'
    _teardown()
  }

  function resetTerminal() {
    if (status.value !== 'running') {
      status.value = 'idle'
      _onMessage?.({ type: 'stdout', data: '' }) // señal de reset al terminal
    }
  }

  // ── Meta ─────────────────────────────────────────────────

  async function checkHealth() {
    try {
      const res = await metaApi.health()
      serverHealth.value = res.status === 'ok'
    } catch {
      serverHealth.value = false
      status.value = 'server_down'
    }
  }

  async function fetchVersion() {
    try {
      const res = await metaApi.version()
      serverVersion.value = res.version
    } catch { /* no crítico */ }
  }

  return {
    code,
    status,
    serverHealth,
    serverVersion,
    ws,
    onWsMessage,
    executeCode,
    sendStdin,
    stopExecution,
    resetTerminal,
    checkHealth,
    fetchVersion,
  }
})