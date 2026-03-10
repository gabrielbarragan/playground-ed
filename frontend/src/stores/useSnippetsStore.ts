import { defineStore } from 'pinia'
import { ref } from 'vue'
import { snippetsApi } from '@/api/snippetsApi'
import type { Snippet } from '@/types/snippets'

export const useSnippetsStore = defineStore('snippets', () => {
  const snippets = ref<Snippet[]>([])
  const activeSnippet = ref<Snippet | null>(null)
  const loading = ref(false)

  async function fetch() {
    loading.value = true
    try {
      snippets.value = await snippetsApi.list()
    } finally {
      loading.value = false
    }
  }

  async function save(title: string, code: string, tags: string[]): Promise<Snippet> {
    const snippet = await snippetsApi.save({ title, code, tags })
    snippets.value.unshift(snippet)
    activeSnippet.value = snippet
    return snippet
  }

  async function update(code: string): Promise<void> {
    if (!activeSnippet.value) return
    const updated = await snippetsApi.update(activeSnippet.value.id, {
      title: activeSnippet.value.title,
      code,
      tags: activeSnippet.value.tags,
    })
    const idx = snippets.value.findIndex(s => s.id === updated.id)
    if (idx !== -1) snippets.value[idx] = updated
    activeSnippet.value = updated
  }

  async function remove(id: string): Promise<void> {
    await snippetsApi.remove(id)
    snippets.value = snippets.value.filter(s => s.id !== id)
    if (activeSnippet.value?.id === id) activeSnippet.value = null
  }

  function load(snippet: Snippet): string {
    activeSnippet.value = snippet
    return snippet.code
  }

  function clearActive() {
    activeSnippet.value = null
  }

  return {
    snippets,
    activeSnippet,
    loading,
    fetch,
    save,
    update,
    remove,
    load,
    clearActive,
  }
})