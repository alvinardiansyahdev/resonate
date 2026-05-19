<template>
  <div
    class="mood-orb"
    :class="{ selected: selected }"
    :style="orbStyle"
    @click="$emit('select', moodId)"
  >
    <div class="orb-glow" />
    <div class="orb-core" />
    <span v-if="showLabel" class="orb-label">{{ label }}</span>
  </div>
</template>

<script setup lang="ts">
import type { MoodId } from "~/types/mood"

const props = withDefaults(defineProps<{
  moodId: MoodId
  label: string
  color: string
  size?: number
  selected?: boolean
  showLabel?: boolean
}>(), {
  size: 48,
  selected: false,
  showLabel: false,
})

defineEmits<{
  select: [id: MoodId]
}>()

const orbStyle = computed(() => ({
  width: `${props.size}px`,
  height: `${props.size}px`,
  "--orb-color": props.color,
}))
</script>

<style scoped>
.mood-orb {
  position: relative;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.3s ease;
}

.mood-orb:hover {
  transform: scale(1.1);
}

.mood-orb.selected {
  transform: scale(1.15);
}

.orb-core {
  width: 60%;
  height: 60%;
  border-radius: 50%;
  background: radial-gradient(circle at 35% 35%, rgba(255,255,255,0.4), var(--orb-color) 60%);
  position: relative;
  z-index: 1;
}

.orb-glow {
  position: absolute;
  inset: -4px;
  border-radius: 50%;
  background: var(--orb-color);
  opacity: 0.2;
  animation: lumen-breathe 4s ease-in-out infinite;
}

.mood-orb.selected .orb-glow {
  opacity: 0.4;
}

.orb-label {
  position: absolute;
  bottom: -20px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.625rem;
  font-family: var(--font-mono);
  color: var(--muted);
  white-space: nowrap;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}
</style>
