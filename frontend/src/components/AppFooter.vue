<template>
  <footer class="app-footer" :class="{ 'app-footer--fixed': fixed }">
    <span class="app-footer__text">
      Desarrollado con <span class="app-footer__heart">❤️</span> por
      <span class="app-footer__author">{{ author }}</span>
      &nbsp;·&nbsp;
      Developed with <span class="app-footer__heart">❤️</span> by
      <span class="app-footer__author">{{ author }}</span>
    </span>
  </footer>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  author?: string
  fixed?: boolean
}>(), {
  author: 'gabobarragan',
  fixed: false,
})
</script>

<style scoped>
.app-footer {
  width: 100%;
  padding: 0.65rem 1.5rem;
  background: #181825;
  border-top: 1px solid #313244;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.app-footer--fixed {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 10;
}

.app-footer__text {
  font-size: 0.7rem;
  color: #45475a;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  letter-spacing: 0.02em;
}

.app-footer__heart {
  font-size: 0.72rem;
}

.app-footer__author {
  color: #cba6f7;
  font-weight: 700;
}
</style>