<template>
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path
      d="M12 0l2.5 7.5L22 9.5l-6 5.5 2 8L12 18l-6 5 2-8-6-5.5 7.5-2z"
      :fill="color"
      :opacity="opacity"
    />
  </svg>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  size?: number
  color?: string
  opacity?: number
}>(), {
  size: 16,
  color: "var(--gold)",
  opacity: 0.6,
})
</script>
