<template>
  <div class="artwork-orb" :style="orbStyle">
    <!-- outer orbit ring -->
    <div class="orbit-ring" />
    <div class="orbit-ring-dashed" />
    <!-- glow halo -->
    <div class="orb-glow" />
    <!-- glass orb body -->
    <div class="orb-body" />
    <!-- specular highlight -->
    <div class="orb-specular" />
    <!-- star decorations -->
    <div class="star top">
      <svg :width="starSize" :height="starSize" viewBox="0 0 14 14">
        <path d="M7 0 L7.6 6.4 L14 7 L7.6 7.6 L7 14 L6.4 7.6 L0 7 L6.4 6.4 Z" fill="var(--gold)" />
      </svg>
    </div>
    <div class="star bottom-right">
      <svg :width="smallStarSize" :height="smallStarSize" viewBox="0 0 14 14">
        <path d="M7 0 L7.6 6.4 L14 7 L7.6 7.6 L7 14 L6.4 7.6 L0 7 L6.4 6.4 Z" fill="#fff" opacity="0.6" />
      </svg>
    </div>
    <div class="star left">
      <svg :width="tinyStarSize" :height="tinyStarSize" viewBox="0 0 14 14">
        <path d="M7 0 L7.6 6.4 L14 7 L7.6 7.6 L7 14 L6.4 7.6 L0 7 L6.4 6.4 Z" fill="var(--gold)" opacity="0.5" />
      </svg>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = withDefaults(defineProps<{
  size?: number
  color?: string
}>(), {
  size: 200,
  color: "var(--accent)",
})

const starSize = computed(() => Math.max(10, props.size * 0.058))
const smallStarSize = computed(() => Math.max(7, props.size * 0.038))
const tinyStarSize = computed(() => Math.max(5, props.size * 0.03))

const orbStyle = computed(() => ({
  width: `${props.size}px`,
  height: `${props.size}px`,
  "--orb-color": props.color,
  "--orb-size": `${props.size}px`,
}))
</script>

<style scoped>
.artwork-orb {
  position: relative;
  border-radius: 50%;
}

.orbit-ring {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 1px solid var(--border);
  animation: lumen-spin 60s linear infinite;
}

.orbit-ring-dashed {
  position: absolute;
  inset: 7%;
  border-radius: 50%;
  border: 1px dashed var(--border);
}

.orb-glow {
  position: absolute;
  inset: -20%;
  border-radius: 50%;
  background: radial-gradient(circle, color-mix(in srgb, var(--orb-color) 30%, transparent) 0%, transparent 60%);
  filter: blur(20px);
}

.orb-body {
  position: absolute;
  inset: 15%;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, #fff 0%, var(--orb-color) 35%, var(--bg-2) 90%);
  box-shadow: 0 30px 60px -10px color-mix(in srgb, var(--orb-color) 31%, transparent), inset 0 0 30px rgba(0, 0, 0, 0.3);
  animation: lumen-breathe 5s ease-in-out infinite;
}

.orb-specular {
  position: absolute;
  top: 20%;
  left: 22%;
  width: 24%;
  height: 18%;
  border-radius: 50%;
  background: radial-gradient(ellipse, rgba(255, 255, 255, 0.7), transparent 70%);
}

.star {
  position: absolute;
  display: flex;
  align-items: center;
  justify-content: center;
}

.star.top {
  top: 2%;
  left: 50%;
  transform: translateX(-50%);
}

.star.bottom-right {
  bottom: 8%;
  right: 12%;
}

.star.left {
  top: 50%;
  left: 0;
}
</style>
