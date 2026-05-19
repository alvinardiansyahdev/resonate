<template>
  <svg
    :width="width"
    :height="height"
    :viewBox="`0 0 ${width} ${height}`"
    xmlns="http://www.w3.org/2000/svg"
  >
    <defs>
      <linearGradient :id="`lw-grad`" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#fff" stop-opacity="0.8" />
        <stop offset="30%" :stop-color="color" stop-opacity="1" />
        <stop offset="100%" :stop-color="color" stop-opacity="0.2" />
      </linearGradient>
    </defs>
    <rect
      v-for="(bar, i) in bars"
      :key="i"
      :x="bar.x"
      :y="(height - bar.h) / 2"
      :width="bar.w"
      :height="bar.h"
      rx="2"
      fill="url(#lw-grad)"
      :opacity="i < splitIdx ? 1 : 0.32"
    >
      <animate
        v-if="active"
        attributeName="height"
        :values="`${bar.h};${bar.target};${bar.h}`"
        :dur="`${bar.dur}s`"
        :begin="`-${bar.delay}s`"
        repeatCount="indefinite"
      />
    </rect>
  </svg>
</template>

<script setup lang="ts">
const props = withDefaults(defineProps<{
  count?: number
  width?: number
  height?: number
  color?: string
  active?: boolean
  split?: number
}>(), {
  count: 60,
  width: 300,
  height: 60,
  color: "var(--accent)",
  active: true,
  split: 0.42,
})

const bars = computed(() => {
  const items = []
  const bw = props.width / props.count
  for (let i = 0; i < props.count; i++) {
    const seed = Math.abs(Math.sin(i * 1.71))
    const wave = Math.abs(Math.sin(i * 0.32))
    const h = Math.max(2, (seed * 0.4 + wave * 0.55) * props.height * 0.9)
    items.push({
      x: i * bw + bw * 0.22,
      w: bw * 0.56,
      h,
      target: h * (0.5 + Math.sin(i) * 0.3),
      dur: 1.6 + (i % 5) * 0.3,
      delay: (i * 0.07) % 2,
    })
  }
  return items
})

const splitIdx = computed(() => Math.floor(props.count * (props.split ?? 0.42)))
</script>
