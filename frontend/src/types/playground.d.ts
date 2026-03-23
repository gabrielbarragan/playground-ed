// ============================================================
// HTTP CONTRACT (POST /api/code-runs)
// ============================================================

export interface CodeExecutionRequest {
  code: string
}

export interface AchievementData {
  id: string
  name: string
  description: string
  icon: string
  points_bonus: number
}

export interface ExecutionResult {
  stdout: string
  stderr: string
  return_code: 0 | 1
  new_achievements?: AchievementData[]
}

export interface ExecutionErrorResponse {
  error: string
}

// ============================================================
// WEBSOCKET PROTOCOL (/ws/run)
// ============================================================

// Cliente → Servidor
export type WsClientMessage =
  | { type: 'run';   code: string }
  | { type: 'stdin'; data: string }
  | { type: 'kill' }

// Comandos gráficos (turtle canvas)
export type GfxCommand =
  | { cmd: 'init';        w: number; h: number }
  | { cmd: 'line';        x1: number; y1: number; x2: number; y2: number; color: string; w: number }
  | { cmd: 'circle';      x: number; y: number; r: number; extent: number; color: string; w: number; pen: boolean }
  | { cmd: 'cursor';      x: number; y: number; a: number }
  | { cmd: 'color';       stroke: string; fill: string }
  | { cmd: 'begin_fill';  color: string }
  | { cmd: 'end_fill' }
  | { cmd: 'clear' }
  | { cmd: 'bgcolor';     color: string }
  | { cmd: 'text';        x: number; y: number; text: string; font: [string, number, string]; color: string }
  | { cmd: 'hide_cursor' | 'show_cursor' | 'done' }

// Servidor → Cliente
export type WsServerMessage =
  | { type: 'stdout';      data: string }
  | { type: 'stderr';      data: string }
  | { type: 'exit';        return_code: 0 | 1 }
  | { type: 'timeout' }
  | { type: 'error';       message: string }
  | { type: 'achievement'; data: AchievementData }
  | { type: 'gfx';         data: GfxCommand }

// ============================================================
// META ENDPOINTS
// ============================================================

export interface HealthResponse  { status: string }
export interface VersionResponse { version: string; message: string }
export interface MetaResponse    { message: string; docs: string }

// ============================================================
// UI STATE
// ============================================================

export type ExecutionStatus =
  | 'idle'
  | 'running'
  | 'success'
  | 'error'
  | 'timeout'
  | 'server_down'

export interface ApiError {
  message: string
  statusCode?: number
  isTimeout: boolean
  isNetworkError: boolean
}