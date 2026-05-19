<template>
  <div class="glass-card" :class="[`elevation-${elevation}`]">
    <slot />
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  elevation?: "low" | "mid" | "high"
}>(), {
  elevation: "mid",
})
</script>

<style scoped>
.glass-card {
  background: var(--surface);
  backdrop-filter: blur(var(--blur-md));
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: var(--space-5);
}

.elevation-low {
  background: rgba(28, 18, 38, 0.35);
  backdrop-filter: blur(var(--blur-sm));
}

.elevation-high {
  background: var(--surface-hi);
  backdrop-filter: blur(var(--blur-lg));
}
</style>
