<template>
  <RouterView />
</template>

<script setup lang="ts">
</script>

<style>
*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html,
body,
#app {
  height: 100%;
  width: 100%;
  font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace;
  background-color: #1e1e2e;
  color: #cdd6f4;
}
</style>