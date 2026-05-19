<template>
  <svg
    class="particle-field"
    :width="width"
    :height="height"
    xmlns="http://www.w3.org/2000/svg"
  >
    <circle
      v-for="(p, i) in particles"
      :key="i"
      :cx="p.x"
      :cy="p.y"
      :r="p.r"
      :fill="color"
      :opacity="p.opacity"
    >
      <animate
        attributeName="opacity"
        :values="`${p.o1};${p.o2};${p.o1}`"
        :dur="`${p.dur}s`"
        repeatCount="indefinite"
      />
    </circle>
  </svg>
</template>

<script setup lang="ts">
interface Particle {
  x: number
  y: number
  r: number
  opacity: number
  o1: number
  o2: number
  dur: number
}

const props = withDefaults(defineProps<{
  count?: number
  color?: string
  seed?: number
}>(), {
  count: 30,
  color: "var(--accent)",
  seed: 42,
})

const width = ref(0)
const height = ref(0)

onMounted(() => {
  width.value = window.innerWidth
  height.value = window.innerHeight
})

const particles = computed<Particle[]>(() => {
  const items: Particle[] = []
  for (let i = 0; i < props.count; i++) {
    const phase = (i * 137.5) % 1
    items.push({
      x: ((i * 89 + props.seed) % width.value) || 200 + i * 30,
      y: ((i * 53 + props.seed) % height.value) || 100 + i * 40,
      r: 1 + (i % 3),
      opacity: 0.1 + phase * 0.5,
      o1: 0.1 + phase * 0.3,
      o2: 0.4 + phase * 0.4,
      dur: 3 + (i % 5),
    })
  }
  return items
})
</script>

<style scoped>
.particle-field {
  position: fixed;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}
</style>
