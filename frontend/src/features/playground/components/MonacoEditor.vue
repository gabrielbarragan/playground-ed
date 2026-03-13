<template>
  <div class="editor-wrapper">
    <div class="editor-pane-header">
      <span class="pane-tab pane-tab--active">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
          <polyline points="14 2 14 8 20 8" />
        </svg>
        main.py
      </span>
    </div>
    <div ref="containerRef" class="monaco-container" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import * as monaco from 'monaco-editor'

const props = defineProps<{ modelValue: string }>()
const emit = defineEmits<{
  'update:modelValue': [value: string]
  run: []
}>()

const containerRef = ref<HTMLDivElement | null>(null)
let editor: monaco.editor.IStandaloneCodeEditor | null = null

function defineTheme() {
  monaco.editor.defineTheme('catppuccin-mocha', {
    base: 'vs-dark',
    inherit: true,
    rules: [
      { token: 'comment', foreground: '6c7086', fontStyle: 'italic' },
      { token: 'keyword', foreground: 'cba6f7', fontStyle: 'bold' },
      { token: 'string', foreground: 'a6e3a1' },
      { token: 'string.escape', foreground: 'fab387' },
      { token: 'number', foreground: 'fab387' },
      { token: 'type', foreground: '89dceb' },
      { token: 'function', foreground: '89b4fa' },
      { token: 'variable', foreground: 'cdd6f4' },
      { token: 'operator', foreground: '89dceb' },
      { token: 'delimiter', foreground: '6c7086' },
      { token: 'delimiter.bracket', foreground: 'cba6f7' },
      { token: 'identifier', foreground: 'cdd6f4' },
    ],
    colors: {
      'editor.background': '#1e1e2e',
      'editor.foreground': '#cdd6f4',
      'editor.lineHighlightBackground': '#2a2a3d',
      'editor.selectionBackground': '#45475a80',
      'editor.inactiveSelectionBackground': '#31324460',
      'editorLineNumber.foreground': '#45475a',
      'editorLineNumber.activeForeground': '#cba6f7',
      'editorCursor.foreground': '#f5e0dc',
      'editorIndentGuide.background1': '#313244',
      'editorIndentGuide.activeBackground1': '#585b70',
      'editorBracketMatch.background': '#45475a50',
      'editorBracketMatch.border': '#cba6f7',
      'editorWidget.background': '#181825',
      'editorWidget.border': '#313244',
      'editorSuggestWidget.background': '#181825',
      'editorSuggestWidget.border': '#313244',
      'editorSuggestWidget.selectedBackground': '#313244',
      'editorHoverWidget.background': '#181825',
      'editorHoverWidget.border': '#313244',
      'scrollbarSlider.background': '#45475a60',
      'scrollbarSlider.hoverBackground': '#585b7080',
      'scrollbarSlider.activeBackground': '#6c708680',
      'scrollbar.shadow': '#00000000',
    },
  })
}

function blockEvent(e: Event) {
  e.preventDefault()
  e.stopPropagation()
}

onMounted(() => {
  if (!containerRef.value) return

  defineTheme()

  // Bloquear click derecho y eventos de portapapeles en el contenedor DOM
  // capture:true para interceptar antes de que Monaco llame stopPropagation()
  containerRef.value.addEventListener('contextmenu', blockEvent, true)
  containerRef.value.addEventListener('copy', blockEvent, true)
  containerRef.value.addEventListener('cut', blockEvent, true)
  containerRef.value.addEventListener('paste', blockEvent, true)

  editor = monaco.editor.create(containerRef.value, {
    value: props.modelValue,
    language: 'python',
    theme: 'catppuccin-mocha',
    fontSize: 14,
    lineHeight: 22,
    fontFamily: "'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace",
    fontLigatures: true,
    minimap: { enabled: false },
    scrollBeyondLastLine: false,
    automaticLayout: true,
    tabSize: 4,
    insertSpaces: true,
    wordWrap: 'on',
    renderLineHighlight: 'gutter',
    smoothScrolling: true,
    cursorBlinking: 'smooth',
    cursorSmoothCaretAnimation: 'on',
    padding: { top: 12, bottom: 12 },
    bracketPairColorization: { enabled: true },
    guides: {
      bracketPairs: true,
      indentation: true,
    },
    suggest: { preview: true },
    contextmenu: false,
    overviewRulerLanes: 0,
    hideCursorInOverviewRuler: true,
    scrollbar: {
      verticalScrollbarSize: 6,
      horizontalScrollbarSize: 6,
    },
  })

  editor.onDidChangeModelContent(() => {
    emit('update:modelValue', editor!.getValue())
  })

  // Ctrl+Enter / Cmd+Enter → ejecutar
  editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
    emit('run')
  })

  // Bloquear copy, cut y paste a nivel de Monaco (teclado y menú de Monaco)
  editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyC, () => {})
  editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyX, () => {})
  editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyV, () => {})
  editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.KeyV, () => {})
})

watch(
  () => props.modelValue,
  (newVal) => {
    if (editor && editor.getValue() !== newVal) {
      editor.setValue(newVal)
    }
  },
)

onBeforeUnmount(() => {
  if (containerRef.value) {
    containerRef.value.removeEventListener('contextmenu', blockEvent, true)
    containerRef.value.removeEventListener('copy', blockEvent, true)
    containerRef.value.removeEventListener('cut', blockEvent, true)
    containerRef.value.removeEventListener('paste', blockEvent, true)
  }
  editor?.dispose()
})
</script>

<style scoped>
.editor-wrapper {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.editor-pane-header {
  display: flex;
  align-items: center;
  background: #181825;
  border-bottom: 1px solid #313244;
  padding: 0 0.5rem;
  flex-shrink: 0;
  height: 36px;
}

.pane-tab {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0 0.75rem;
  height: 100%;
  font-size: 0.75rem;
  color: #6c7086;
  border-bottom: 2px solid transparent;
  cursor: default;
  user-select: none;
}

.pane-tab--active {
  color: #cdd6f4;
  border-bottom-color: #cba6f7;
}

.pane-tab svg {
  opacity: 0.7;
}

.monaco-container {
  flex: 1;
  min-height: 0;
  width: 100%;
}
</style>