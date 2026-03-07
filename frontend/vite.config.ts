import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import monacoEditorPlugin from 'vite-plugin-monaco-editor'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  const backendUrl = env['VITE_BACKEND_URL'] ?? 'http://localhost:8000'
  const wsUrl      = env['VITE_WS_URL']      ?? 'ws://localhost:8000'

  return {
    plugins: [
      vue(),
      monacoEditorPlugin({
        languageWorkers: ['editorWorkerService', 'typescript', 'json'],
        customWorkers: [
          {
            label: 'python',
            entry: 'monaco-editor/esm/vs/basic-languages/python/python.contribution',
          },
        ],
      }),
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    server: {
      port: 5173,
      proxy: {
        '/api': {
          target: backendUrl,
          changeOrigin: true,
        },
        '/ws': {
          target: wsUrl,
          ws: true,
          changeOrigin: true,
        },
      },
    },
  }
})