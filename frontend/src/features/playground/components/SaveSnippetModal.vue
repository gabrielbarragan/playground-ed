<template>
  <Teleport to="body">
    <div class="modal-backdrop" @click.self="$emit('close')">
      <div class="modal">
        <div class="modal-header">
          <h2 class="modal-title">Guardar Snippet</h2>
          <button class="modal-close" @click="$emit('close')">✕</button>
        </div>

        <form @submit.prevent="handleSave">
          <div class="form-group">
            <label class="form-label">Título</label>
            <input
              ref="titleInput"
              v-model="title"
              type="text"
              class="form-input"
              placeholder="Ej: Ordenamiento burbuja"
              maxlength="200"
              required
            />
          </div>

          <div class="form-group">
            <label class="form-label">Tags <span class="label-hint">(separados por coma)</span></label>
            <input
              v-model="tagsRaw"
              type="text"
              class="form-input"
              placeholder="Ej: algoritmos, listas"
            />
          </div>

          <p v-if="error" class="form-error">{{ error }}</p>

          <div class="modal-actions">
            <button type="button" class="btn-cancel" @click="$emit('close')">Cancelar</button>
            <button type="submit" class="btn-save" :disabled="loading">
              <span v-if="loading" class="spinner" />
              {{ loading ? 'Guardando...' : 'Guardar' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useSnippetsStore } from '@/stores/useSnippetsStore'

const props = defineProps<{ code: string }>()
const emit = defineEmits<{ close: []; saved: [] }>()

const store = useSnippetsStore()
const title = ref('')
const tagsRaw = ref('')
const loading = ref(false)
const error = ref('')
const titleInput = ref<HTMLInputElement | null>(null)

onMounted(() => titleInput.value?.focus())

async function handleSave() {
  error.value = ''
  const tags = tagsRaw.value
    .split(',')
    .map(t => t.trim())
    .filter(Boolean)

  loading.value = true
  try {
    await store.save(title.value.trim(), props.code, tags)
    emit('saved')
    emit('close')
  } catch {
    error.value = 'No se pudo guardar el snippet. Intentá de nuevo.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: #00000080;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  backdrop-filter: blur(2px);
}

.modal {
  width: 100%;
  max-width: 420px;
  background: #181825;
  border: 1px solid #313244;
  border-radius: 12px;
  padding: 1.5rem;
  margin: 1rem;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.25rem;
}

.modal-title {
  font-size: 1rem;
  font-weight: 700;
  color: #cdd6f4;
}

.modal-close {
  background: transparent;
  border: none;
  color: #6c7086;
  font-size: 0.85rem;
  cursor: pointer;
  padding: 0.25rem;
  line-height: 1;
  transition: color 0.15s;
}

.modal-close:hover { color: #cdd6f4; }

.form-group { margin-bottom: 1rem; }

.form-label {
  display: block;
  font-size: 0.78rem;
  color: #a6adc8;
  margin-bottom: 0.4rem;
  font-weight: 500;
}

.label-hint {
  color: #45475a;
  font-weight: 400;
}

.form-input {
  width: 100%;
  padding: 0.6rem 0.85rem;
  background: #1e1e2e;
  border: 1px solid #313244;
  border-radius: 7px;
  color: #cdd6f4;
  font-family: inherit;
  font-size: 0.88rem;
  outline: none;
  transition: border-color 0.15s;
  box-sizing: border-box;
}

.form-input::placeholder { color: #45475a; }
.form-input:focus { border-color: #cba6f7; }

.form-error {
  font-size: 0.78rem;
  color: #f38ba8;
  margin-bottom: 0.75rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.6rem;
  margin-top: 0.5rem;
}

.btn-cancel {
  padding: 0.5rem 1rem;
  background: transparent;
  color: #6c7086;
  border: 1px solid #313244;
  border-radius: 7px;
  font-size: 0.85rem;
  font-family: inherit;
  cursor: pointer;
  transition: border-color 0.15s, color 0.15s;
}

.btn-cancel:hover { border-color: #585b70; color: #a6adc8; }

.btn-save {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 1.2rem;
  background: #cba6f7;
  color: #1e1e2e;
  border: none;
  border-radius: 7px;
  font-size: 0.85rem;
  font-weight: 700;
  font-family: inherit;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-save:hover:not(:disabled) { background: #d4b4ff; }
.btn-save:disabled { opacity: 0.5; cursor: not-allowed; }

.spinner {
  width: 12px;
  height: 12px;
  border: 2px solid #1e1e2e60;
  border-top-color: #1e1e2e;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }
</style>