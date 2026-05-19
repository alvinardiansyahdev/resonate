<template>
  <div class="chapter-dots">
    <div
      v-for="(wp, i) in waypoints"
      :key="i"
      class="dot-group"
      :class="{ completed: i < current, active: i === current }"
    >
      <div
        class="dot"
        :class="{ active: i === current, completed: i < current }"
      />
      <span
        class="dot-label mono"
        :class="{ active: i === current, completed: i < current }"
      >{{ romanNumeral(i + 1) }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ArcWaypoint } from "~/types/arc"

defineProps<{
  waypoints: ArcWaypoint[]
  current: number
}>()

function romanNumeral(n: number): string {
  const map = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]
  return map[n - 1] ?? String(n)
}
</script>

<style scoped>
.chapter-dots {
  display: flex;
  justify-content: space-between;
  width: 100%;
  padding: 0 4px;
}

.dot-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 999px;
  background: var(--border);
  transition: all 0.3s;
}

.dot.active {
  background: var(--gold);
  box-shadow: 0 0 6px var(--gold);
}

.dot.completed {
  background: color-mix(in srgb, var(--accent) 50%, transparent);
}

.dot-label {
  font-size: 8px;
  color: var(--faint);
  letter-spacing: 0.1em;
  transition: all 0.3s;
}

.dot-label.active {
  color: var(--gold);
}

.dot-label.completed {
  color: var(--muted);
}
</style>
