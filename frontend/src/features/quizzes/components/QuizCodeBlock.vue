<template>
  <pre class="quiz-code-block"><code>{{ code }}</code></pre>
</template>

<script setup lang="ts">
defineProps<{ code: string }>()
</script>

<style scoped>
.quiz-code-block {
  margin: 0.75rem 0;
  padding: 1rem 1.25rem;
  background: #181825;
  border: 1px solid #313244;
  border-radius: 8px;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 0.82rem;
  color: #cdd6f4;
  overflow-x: auto;
  white-space: pre;
  line-height: 1.6;
}
</style>