<template>
  <div class="canvas-wrapper">
    <div class="canvas-pane-header">
      <span class="pane-label">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="18" height="18" rx="2" />
          <circle cx="8.5" cy="8.5" r="1.5" fill="currentColor" stroke="none" />
          <polyline points="21 15 16 10 5 21" />
        </svg>
        Canvas
      </span>
      <button class="btn-canvas-clear" @click="clearCanvas" title="Limpiar canvas">
        <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="3 6 5 6 21 6" />
          <path d="M19 6l-1 14H6L5 6" />
          <path d="M10 11v6M14 11v6" />
          <path d="M9 6V4h6v2" />
        </svg>
      </button>
    </div>

    <div class="canvas-scroll">
      <div class="canvas-container" :style="{ width: canvasW + 'px', height: canvasH + 'px' }">
        <!-- Capa de dibujo -->
        <canvas ref="drawRef" :width="canvasW" :height="canvasH" class="canvas-draw" />
        <!-- Capa de cursor (overlay) -->
        <canvas ref="cursorRef" :width="canvasW" :height="canvasH" class="canvas-cursor" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { GfxCommand } from '@/types/playground'

// ── Canvas refs ───────────────────────────────────────────────────────────────
const drawRef   = ref<HTMLCanvasElement | null>(null)
const cursorRef = ref<HTMLCanvasElement | null>(null)

const canvasW = ref(600)
const canvasH = ref(400)

// ── State interno del renderer ────────────────────────────────────────────────
let strokeColor  = '#000000'
let fillColor    = '#000000'
let lineWidth    = 1
let filling      = false
let fillPath: Array<{ x: number; y: number }> = []
let showCursor   = true
let cursorX      = 0
let cursorY      = 0
let cursorAngle  = 90  // grados

// ── Helpers de coordenadas (origen en el centro) ──────────────────────────────
function toScreen(x: number, y: number): [number, number] {
  return [canvasW.value / 2 + x, canvasH.value / 2 - y]
}

function getCtx(): CanvasRenderingContext2D | null {
  return drawRef.value?.getContext('2d') ?? null
}

// ── Dibujar cursor (tortuga) ──────────────────────────────────────────────────
function drawCursor() {
  const cv = cursorRef.value
  if (!cv) return
  const ctx = cv.getContext('2d')!
  ctx.clearRect(0, 0, canvasW.value, canvasH.value)
  if (!showCursor) return

  const [sx, sy] = toScreen(cursorX, cursorY)
  const rad = (cursorAngle * Math.PI) / 180

  ctx.save()
  ctx.translate(sx, sy)
  ctx.rotate(-rad + Math.PI / 2)  // ajuste: 90° arriba en coordenadas turtle = arriba en canvas

  // Triángulo pequeño como cursor
  ctx.beginPath()
  ctx.moveTo(0, -10)
  ctx.lineTo(6, 8)
  ctx.lineTo(-6, 8)
  ctx.closePath()
  ctx.fillStyle = '#a6e3a1'
  ctx.strokeStyle = '#313244'
  ctx.lineWidth = 1.5
  ctx.fill()
  ctx.stroke()
  ctx.restore()
}

// ── Comando: limpiar ──────────────────────────────────────────────────────────
function clearCanvas() {
  const ctx = getCtx()
  if (!ctx) return
  ctx.clearRect(0, 0, canvasW.value, canvasH.value)
  drawCursor()
}

// ── Procesador de comandos GFX ────────────────────────────────────────────────
function handleGfxCommand(cmd: GfxCommand) {
  const ctx = getCtx()
  if (!ctx) return

  switch (cmd.cmd) {
    case 'init': {
      canvasW.value = cmd.w
      canvasH.value = cmd.h
      // Limpiar en el siguiente tick (canvas se redimensiona)
      setTimeout(() => {
        getCtx()?.clearRect(0, 0, cmd.w, cmd.h)
        cursorX = 0; cursorY = 0; cursorAngle = 90
        drawCursor()
      }, 0)
      break
    }

    case 'line': {
      const [x1s, y1s] = toScreen(cmd.x1, cmd.y1)
      const [x2s, y2s] = toScreen(cmd.x2, cmd.y2)
      ctx.beginPath()
      ctx.moveTo(x1s, y1s)
      ctx.lineTo(x2s, y2s)
      ctx.strokeStyle = cmd.color
      ctx.lineWidth   = cmd.w
      ctx.lineCap     = 'round'
      ctx.stroke()
      if (filling) {
        fillPath.push({ x: cmd.x2, y: cmd.y2 })
      }
      break
    }

    case 'circle': {
      if (!cmd.pen) break
      const [sx, sy] = toScreen(cmd.x, cmd.y)
      const startAngle = 0
      const endAngle   = (cmd.extent / 360) * Math.PI * 2
      ctx.beginPath()
      ctx.arc(sx, sy - cmd.r, Math.abs(cmd.r), startAngle, endAngle)
      ctx.strokeStyle = cmd.color
      ctx.lineWidth   = cmd.w
      ctx.stroke()
      break
    }

    case 'cursor': {
      cursorX = cmd.x
      cursorY = cmd.y
      cursorAngle = cmd.a
      drawCursor()
      break
    }

    case 'color': {
      strokeColor = cmd.stroke
      fillColor   = cmd.fill
      break
    }

    case 'begin_fill': {
      filling  = true
      fillPath = []
      break
    }

    case 'end_fill': {
      if (fillPath.length > 1) {
        ctx.beginPath()
        const [fx, fy] = toScreen(fillPath[0].x, fillPath[0].y)
        ctx.moveTo(fx, fy)
        for (let i = 1; i < fillPath.length; i++) {
          const [px, py] = toScreen(fillPath[i].x, fillPath[i].y)
          ctx.lineTo(px, py)
        }
        ctx.closePath()
        ctx.fillStyle = fillColor
        ctx.fill()
      }
      filling  = false
      fillPath = []
      break
    }

    case 'clear': {
      ctx.clearRect(0, 0, canvasW.value, canvasH.value)
      drawCursor()
      break
    }

    case 'bgcolor': {
      const cv = drawRef.value
      if (cv) cv.style.background = cmd.color
      break
    }

    case 'text': {
      const [sx, sy] = toScreen(cmd.x, cmd.y)
      const [family, size, style] = cmd.font
      ctx.font      = `${style} ${size}px ${family}`
      ctx.fillStyle = cmd.color
      ctx.fillText(cmd.text, sx, sy)
      break
    }

    case 'hide_cursor': {
      showCursor = false
      drawCursor()
      break
    }

    case 'show_cursor': {
      showCursor = true
      drawCursor()
      break
    }

    case 'done': {
      // no-op: el canvas ya está visible
      break
    }
  }
}

// ── Reset completo (nueva ejecución) ──────────────────────────────────────────
function reset() {
  strokeColor = '#000000'
  fillColor   = '#000000'
  lineWidth   = 1
  filling     = false
  fillPath    = []
  showCursor  = true
  cursorX     = 0
  cursorY     = 0
  cursorAngle = 90
  if (drawRef.value) drawRef.value.style.background = ''
  clearCanvas()
}

onMounted(() => {
  drawCursor()
})

defineExpose({ handleGfxCommand, reset })
</script>

<style scoped>
.canvas-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #181825;
}

.canvas-pane-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.4rem 0.75rem;
  border-bottom: 1px solid #313244;
  flex-shrink: 0;
}

.pane-label {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.72rem;
  font-weight: 600;
  color: #6c7086;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.btn-canvas-clear {
  background: none;
  border: 1px solid #313244;
  border-radius: 4px;
  color: #6c7086;
  cursor: pointer;
  padding: 2px 6px;
  display: flex;
  align-items: center;
  transition: color 0.15s, border-color 0.15s;
}

.btn-canvas-clear:hover {
  color: #cdd6f4;
  border-color: #585b70;
}

.canvas-scroll {
  flex: 1;
  overflow: auto;
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  padding: 0.75rem;
}

.canvas-container {
  position: relative;
  border: 1px solid #313244;
  border-radius: 6px;
  overflow: hidden;
  background: #ffffff;
  flex-shrink: 0;
}

.canvas-draw,
.canvas-cursor {
  position: absolute;
  top: 0;
  left: 0;
}

.canvas-draw   { z-index: 1; }
.canvas-cursor { z-index: 2; pointer-events: none; }
</style>
