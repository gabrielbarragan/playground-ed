// ============================================================
// HTTP CONTRACT (POST /api/code-runs)
// ============================================================

export interface CodeExecutionRequest {
  code: string
}

export interface ExecutionResult {
  stdout: string
  stderr: string
  return_code: 0 | 1
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

// Servidor → Cliente
export type WsServerMessage =
  | { type: 'stdout';  data: string }
  | { type: 'stderr';  data: string }
  | { type: 'exit';    return_code: 0 | 1 }
  | { type: 'timeout' }
  | { type: 'error';   message: string }

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