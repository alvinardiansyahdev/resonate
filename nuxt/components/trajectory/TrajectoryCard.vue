<template>
  <div class="trajectory-card" :class="{ selected }" @click="$emit('select')">
    <div v-if="selected" class="selected-star">
      <svg width="10" height="10" viewBox="0 0 14 14">
        <path d="M7 0 L7.6 6.4 L14 7 L7.6 7.6 L7 14 L6.4 7.6 L0 7 L6.4 6.4 Z" fill="var(--gold)" />
      </svg>
    </div>

    <div class="card-top">
      <span class="chapter-mono mono">CHAPTER {{ romanNum }}</span>
      <div class="mini-ribbon">
        <span class="dot" :style="{ background: fromColor, boxShadow: `0 0 6px ${fromColor}` }" />
        <span class="ribbon-line" :style="{ background: `linear-gradient(90deg, ${fromColor}, ${toColor})` }" />
        <span class="dot" :style="{ background: toColor, boxShadow: `0 0 6px ${toColor}` }" />
      </div>
    </div>

    <h3 class="card-title serif-i">{{ label }}</h3>
    <p class="card-desc">{{ desc }}</p>
  </div>
</template>

<script setup lang="ts">
import type { MoodId } from "~/types/mood"

const props = defineProps<{
  label: string
  desc: string
  fromLabel: string
  toLabel: string
  shape: string
  selected?: boolean
  num?: number
}>()

defineEmits<{
  select: []
}>()

const MOOD_COLORS: Record<string, string> = {
  sadness: "#60a5fa", joy: "#facc15", anger: "#f87171",
  calm: "#4ade80", energy: "#fb923c", love: "#f472b6",
  fear: "#a78bfa", neutral: "#8888a0",
}

const fromColor = computed(() => {
  const key = props.fromLabel.toLowerCase()
  return MOOD_COLORS[key] ?? "#c084fc"
})

const toColor = computed(() => {
  const key = props.toLabel.toLowerCase()
  return MOOD_COLORS[key] ?? "#c084fc"
})

const romanNum = computed(() => {
  const n = props.num ?? 1
  const map = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]
  return map[n - 1] ?? String(n)
})
</script>

<style scoped>
.trajectory-card {
  position: relative;
  padding: 18px 22px;
  border-radius: 16px;
  border: 1px solid var(--border);
  background: rgba(28, 18, 38, 0.5);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  cursor: pointer;
  overflow: hidden;
  transition: border-color 0.2s, background 0.2s;
}

.trajectory-card:hover {
  border-color: var(--border-hi);
}

.trajectory-card.selected {
  background: linear-gradient(135deg, rgba(192, 132, 252, 0.14), rgba(232, 200, 135, 0.06));
  border-color: color-mix(in srgb, var(--accent) 31%, transparent);
}

.selected-star {
  position: absolute;
  right: 14px;
  top: 14px;
  display: flex;
  gap: 4px;
}

.card-top {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
}

.chapter-mono {
  font-size: 10px;
  color: var(--faint);
  letter-spacing: 0.25em;
}

.trajectory-card.selected .chapter-mono {
  color: var(--gold);
}

.mini-ribbon {
  display: flex;
  align-items: center;
  gap: 6px;
}

.dot {
  width: 7px;
  height: 7px;
  border-radius: 999px;
  flex-shrink: 0;
}

.ribbon-line {
  width: 60px;
  height: 1px;
  border-radius: 1px;
}

.card-title {
  font-size: 26px;
  line-height: 1.1;
  margin-top: 6px;
  color: rgba(245, 235, 250, 0.88);
}

.trajectory-card.selected .card-title {
  color: var(--text-hi);
}

.card-desc {
  font-size: 12px;
  color: var(--muted);
  margin-top: 4px;
  font-style: italic;
}
</style>
