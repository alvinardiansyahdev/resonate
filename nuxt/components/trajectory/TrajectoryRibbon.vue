<template>
  <svg
    :width="width"
    :height="height"
    :viewBox="`0 0 ${width} ${height}`"
    xmlns="http://www.w3.org/2000/svg"
  >
    <defs>
      <linearGradient :id="gradId" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0%" :stop-color="fromColor" />
        <stop offset="100%" :stop-color="toColor" />
      </linearGradient>
      <filter :id="glowId" x="-100%" y="-100%" width="300%" height="300%">
        <feGaussianBlur stdDeviation="4" />
      </filter>
    </defs>

    <!-- outer halo glow -->
    <path
      :d="pathD"
      :stroke="`url(#${gradId})`"
      stroke-width="14"
      fill="none"
      opacity="0.25"
      :filter="`url(#${glowId})`"
      stroke-linecap="round"
    />
    <!-- crisp center line -->
    <path
      :d="pathD"
      :stroke="`url(#${gradId})`"
      stroke-width="1.8"
      fill="none"
      stroke-linecap="round"
    />

    <!-- start orb -->
    <circle :cx="16" :cy="startPoint.y" r="9" :fill="fromColor" opacity="0.5" :filter="`url(#${glowId})`" />
    <circle :cx="16" :cy="startPoint.y" r="6" :fill="fromColor">
      <animate attributeName="r" values="6;7.5;6" dur="3s" repeatCount="indefinite" />
    </circle>
    <ellipse :cx="14" :cy="startPoint.y - 2" rx="2.4" ry="1.4" fill="#fff" opacity="0.6" />

    <!-- end orb -->
    <circle :cx="width - 16" :cy="endPoint.y" r="9" :fill="toColor" opacity="0.5" :filter="`url(#${glowId})`" />
    <circle :cx="width - 16" :cy="endPoint.y" r="6" :fill="toColor">
      <animate attributeName="r" values="6;7.5;6" dur="3s" begin="-1.5s" repeatCount="indefinite" />
    </circle>
    <ellipse :cx="width - 18" :cy="endPoint.y - 2" rx="2.4" ry="1.4" fill="#fff" opacity="0.6" />

    <!-- drifting glow dot -->
    <circle r="4" fill="#fff" opacity="0.9">
      <animateMotion dur="6s" repeatCount="indefinite" :path="pathD" />
    </circle>
  </svg>
</template>

<script setup lang="ts">
import type { MoodId } from "~/types/mood"

const props = withDefaults(defineProps<{
  fromMood: MoodId
  toMood: MoodId
  width?: number
  height?: number
}>(), {
  width: 380,
  height: 110,
})

const uid = Math.random().toString(36).slice(2, 7)
const gradId = computed(() => `tr-grad-${uid}`)
const glowId = computed(() => `tr-glow-${uid}`)

const MOOD_COLORS: Record<MoodId, string> = {
  sadness: "#60a5fa",
  joy: "#facc15",
  anger: "#f87171",
  calm: "#4ade80",
  energy: "#fb923c",
  love: "#f472b6",
  fear: "#a78bfa",
  neutral: "#8888a0",
}

const fromColor = computed(() => MOOD_COLORS[props.fromMood] ?? "#c084fc")
const toColor = computed(() => MOOD_COLORS[props.toMood] ?? "#c084fc")

function sigmoid(t: number, k = 7) {
  const x = (t - 0.5) * k
  return 1 / (1 + Math.exp(-x))
}

const points = computed(() => {
  const n = 50
  const pts: Array<{ t: number; y: number }> = []
  for (let i = 0; i < n; i++) {
    const t = i / (n - 1)
    const y = props.height * 0.78 + (props.height * 0.22 - props.height * 0.78) * sigmoid(t, 7)
    pts.push({ t, y })
  }
  return pts
})

const pathD = computed(() => {
  return points.value.map((p, i) => `${i === 0 ? "M" : "L"} ${p.t * (props.width - 32) + 16} ${p.y}`).join(" ")
})

const startPoint = computed(() => ({ y: points.value[0]?.y ?? props.height * 0.78 }))
const endPoint = computed(() => ({ y: points.value[points.value.length - 1]?.y ?? props.height * 0.22 }))
</script>
