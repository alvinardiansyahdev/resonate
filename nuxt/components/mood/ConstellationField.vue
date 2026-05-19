<template>
  <div class="constellation" :style="containerStyle">
    <svg
      ref="svgRef"
      :width="width"
      :height="height"
      :viewBox="`0 0 ${width} ${height}`"
      :style="{ overflow: 'visible', display: 'block', ...parallaxStyle }"
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        <!-- Per-mood smooth aura gradient: transparent center → glow peak → transparent edge -->
        <radialGradient
          v-for="m in moodData" :key="`ag-${m.id}`"
          :id="`aura-g-${uid}-${m.id}`" cx="50%" cy="50%"
        >
          <stop offset="0%"   :stop-color="m.color" stop-opacity="0"    />
          <stop offset="15%"  :stop-color="m.color" stop-opacity="1"    />
          <stop offset="38%"  :stop-color="m.color" stop-opacity="0.55" />
          <stop offset="68%"  :stop-color="m.color" stop-opacity="0.18" />
          <stop offset="100%" :stop-color="m.color" stop-opacity="0"    />
        </radialGradient>

        <!-- Per-mood orb gradient: white-hot core → mood color -->
        <radialGradient
          v-for="m in moodData" :key="`og-${m.id}`"
          :id="`orb-g-${uid}-${m.id}`" cx="35%" cy="32%"
        >
          <stop offset="0%"   stop-color="#ffffff" stop-opacity="0.95" />
          <stop offset="30%"  :stop-color="m.color" stop-opacity="1"   />
          <stop offset="80%"  :stop-color="m.color" stop-opacity="0.70" />
          <stop offset="100%" :stop-color="m.color" stop-opacity="0.30" />
        </radialGradient>

        <!-- Blur for ribbon glow underlay -->
        <filter :id="`blur-${uid}`" x="-100%" y="-100%" width="300%" height="300%">
          <feGaussianBlur stdDeviation="4" />
        </filter>

        <!-- Ribbon gradient — userSpaceOnUse so it always flows from→to regardless of direction -->
        <linearGradient
          v-if="target && modelValue && target !== modelValue"
          :id="`ribbon-grad-${uid}`"
          gradientUnits="userSpaceOnUse"
          :x1="points[modelValue].x" :y1="points[modelValue].y"
          :x2="points[target].x"     :y2="points[target].y"
        >
          <stop offset="0%"   :stop-color="fromColor" />
          <stop offset="100%" :stop-color="toColor" />
        </linearGradient>
      </defs>

      <!-- Edge connection lines (constellation skeleton) -->
      <g v-for="(edge, i) in edges" :key="i">
        <line
          :x1="points[edge.from].x" :y1="points[edge.from].y"
          :x2="points[edge.to].x"   :y2="points[edge.to].y"
          :stroke="edge.isSel ? selColor : '#7c6fa0'"
          :stroke-width="edge.isSel ? 1.2 : 0.6"
          :opacity="edge.isSel ? 0.60 : 0.20"
          :stroke-dasharray="edge.isSel ? 'none' : '2 6'"
        />
      </g>

      <!-- Trajectory ribbon -->
      <g v-if="target && modelValue && target !== modelValue">
        <path
          :class="`ribbon-glow-${uid}`"
          :d="ribbonPath"
          :stroke="`url(#ribbon-grad-${uid})`"
          stroke-width="16" fill="none" opacity="0.20"
          :filter="`url(#blur-${uid})`"
          stroke-linecap="round" pathLength="1"
          stroke-dasharray="1" stroke-dashoffset="1"
        />
        <path
          :class="`ribbon-line-${uid}`"
          :d="ribbonPath"
          :stroke="`url(#ribbon-grad-${uid})`"
          stroke-width="1.5" fill="none"
          stroke-linecap="round" pathLength="1"
          stroke-dasharray="1" stroke-dashoffset="1"
        />
        <circle r="3" fill="#fff" opacity="0.85">
          <animateMotion dur="5s" repeatCount="indefinite" :path="ribbonPath" />
        </circle>
      </g>

      <!-- Mood nodes: smooth nebula aura + glowing orb -->
      <g v-for="(m, i) in moodData" :key="m.id">

        <!-- Smooth nebula aura — single gradient circle, soft breathing -->
        <circle
          :cx="points[m.id].x" :cy="points[m.id].y"
          :fill="`url(#aura-g-${uid}-${m.id})`"
          :opacity="m.id === modelValue ? 0.55 : 0.18"
          pointer-events="none"
          r="0"
        >
          <animate attributeName="r"
            :values="m.id === modelValue
              ? `${auraR(m.id)};${auraR(m.id) * 1.08};${auraR(m.id)}`
              : `${auraR(m.id)};${auraR(m.id) * 1.06};${auraR(m.id)}`"
            :dur="`${7 + i * 0.6}s`" :begin="`-${i * 0.9}s`"
            repeatCount="indefinite"
          />
          <animate v-if="m.id !== modelValue"
            attributeName="opacity"
            values="0.13;0.22;0.13"
            :dur="`${7 + i * 0.6}s`" :begin="`-${i * 0.9}s`"
            repeatCount="indefinite"
          />
        </circle>

        <!-- Subtle pulse ring (selected only) -->
        <circle
          v-if="m.id === modelValue"
          :cx="points[m.id].x" :cy="points[m.id].y"
          fill="none" :stroke="m.color" stroke-width="0.7"
          pointer-events="none"
          r="0"
        >
          <animate attributeName="r"
            :values="`${orbR(m.id) + 4};${orbR(m.id) + 38};${orbR(m.id) + 4}`"
            dur="4s" repeatCount="indefinite" />
          <animate attributeName="opacity" values="0.45;0;0.45" dur="4s" repeatCount="indefinite" />
        </circle>

        <!-- Glowing orb core (gradient, breathing) -->
        <circle
          :cx="points[m.id].x" :cy="points[m.id].y"
          :fill="`url(#orb-g-${uid}-${m.id})`"
          pointer-events="none"
          r="0"
        >
          <animate attributeName="r"
            :values="`${orbR(m.id)};${orbR(m.id) * 1.05};${orbR(m.id)}`"
            :dur="`${5 + i * 0.4}s`" :begin="`-${i * 0.5}s`"
            repeatCount="indefinite"
          />
        </circle>

        <!-- Specular highlight -->
        <ellipse
          :cx="points[m.id].x - orbR(m.id) * 0.28"
          :cy="points[m.id].y - orbR(m.id) * 0.26"
          :rx="orbR(m.id) * 0.35"
          :ry="orbR(m.id) * 0.20"
          fill="#fff"
          :opacity="m.id === modelValue ? 0.38 : 0.25"
          pointer-events="none"
        />

        <!-- Invisible hit target -->
        <circle
          :cx="points[m.id].x" :cy="points[m.id].y"
          :r="hitR(m.id)"
          fill="transparent"
          class="mood-orb"
          :class="{ selected: m.id === modelValue, is_target: m.id === target }"
          @click="select(m.id)"
        />

        <!-- Label -->
        <text
          :x="points[m.id].x"
          :y="points[m.id].y + orbR(m.id) + (m.id === modelValue ? 20 : 14)"
          text-anchor="middle"
          :font-family="m.id === modelValue ? 'Instrument Serif, serif' : 'JetBrains Mono, monospace'"
          :font-style="m.id === modelValue ? 'italic' : 'normal'"
          :font-size="m.id === modelValue ? 22 : 11"
          :fill="m.id === modelValue ? 'var(--text-hi)' : 'var(--muted)'"
          class="mood-label"
        >{{ m.label }}</text>

        <text
          v-if="m.id === modelValue"
          :x="points[m.id].x"
          :y="points[m.id].y + orbR(m.id) + 33"
          text-anchor="middle"
          font-family="JetBrains Mono, monospace"
          font-size="8"
          fill="var(--gold)"
          letter-spacing="0.2em"
        >★ NOW</text>
      </g>
    </svg>
  </div>
</template>

<script setup lang="ts">
import { animate } from "animejs"
import type { MoodId } from "~/types/mood"

const props = withDefaults(defineProps<{
  modelValue: MoodId
  target?: MoodId
  width?: number
  height?: number
  interactive?: boolean
}>(), {
  width: 400,
  height: 400,
  interactive: true,
})

const emit = defineEmits<{
  "update:modelValue": [id: MoodId]
  "update:target":     [id: MoodId | undefined]
  tracePath:           [payload: { from: MoodId; to: MoodId }]
}>()

const moodStore = useMood()
const uid       = Math.random().toString(36).slice(2, 7)
const svgRef    = ref<SVGSVGElement | null>(null)

// ─── Mouse parallax ───────────────────────────────────────────────────────────
const parallaxX       = ref(0)
const parallaxY       = ref(0)
const parallaxTarget  = { x: 0, y: 0 }
const parallaxCurrent = { x: 0, y: 0 }
let rafId: number | null = null

function parallaxTick() {
  parallaxCurrent.x += (parallaxTarget.x - parallaxCurrent.x) * 0.055
  parallaxCurrent.y += (parallaxTarget.y - parallaxCurrent.y) * 0.055
  parallaxX.value = parallaxCurrent.x
  parallaxY.value = parallaxCurrent.y
  rafId = requestAnimationFrame(parallaxTick)
}

function onMouseMove(e: MouseEvent) {
  parallaxTarget.x = (e.clientX / window.innerWidth  - 0.5) * 2 * 18
  parallaxTarget.y = (e.clientY / window.innerHeight - 0.5) * 2 * 18
}

onMounted(() => {
  window.addEventListener('mousemove', onMouseMove, { passive: true })
  rafId = requestAnimationFrame(parallaxTick)
})
onUnmounted(() => {
  window.removeEventListener('mousemove', onMouseMove)
  if (rafId !== null) cancelAnimationFrame(rafId)
})

const parallaxStyle = computed(() => ({
  transform: `translate(${parallaxX.value}px, ${parallaxY.value}px)`,
  willChange: 'transform',
}))

// ─── Mood data ────────────────────────────────────────────────────────────────
const moodData = [
  { id: "sadness" as MoodId, label: "Sadness", color: "#60a5fa" },
  { id: "joy"     as MoodId, label: "Joy",     color: "#facc15" },
  { id: "anger"   as MoodId, label: "Anger",   color: "#f87171" },
  { id: "calm"    as MoodId, label: "Calm",    color: "#4ade80" },
  { id: "energy"  as MoodId, label: "Energy",  color: "#fb923c" },
  { id: "love"    as MoodId, label: "Love",    color: "#f472b6" },
  { id: "fear"    as MoodId, label: "Fear",    color: "#a78bfa" },
  { id: "neutral" as MoodId, label: "Neutral", color: "#8888a0" },
]

// Scattered constellation layout (organic, not a ring)
const POSITIONS: Record<MoodId, [number, number]> = {
  sadness: [0.18, 0.30],
  joy:     [0.78, 0.20],
  anger:   [0.84, 0.54],
  calm:    [0.30, 0.76],
  energy:  [0.62, 0.30],
  love:    [0.50, 0.52],
  fear:    [0.15, 0.62],
  neutral: [0.54, 0.80],
}

const points = computed((): Record<MoodId, { x: number; y: number }> => {
  const p = {} as Record<MoodId, { x: number; y: number }>
  for (const m of moodData) {
    const [rx, ry] = POSITIONS[m.id]
    p[m.id] = { x: rx * props.width, y: ry * props.height }
  }
  return p
})

const selColor  = computed(() => moodData.find(m => m.id === props.modelValue)?.color ?? "#c084fc")
const fromColor = computed(() => moodData.find(m => m.id === props.modelValue)?.color ?? "#c084fc")
const toColor   = computed(() => props.target
  ? (moodData.find(m => m.id === props.target)?.color ?? "#c084fc")
  : "#c084fc"
)

// ─── Node sizing (scales with viewport) ──────────────────────────────────────
const S = computed(() => props.width / 400)

function orbR(id: MoodId)  { return (id === props.modelValue ? 19  : 9)  * S.value }
function auraR(id: MoodId) { return (id === props.modelValue ? 100 : 40) * S.value }
function hitR(id: MoodId)  { return (id === props.modelValue ? 28  : 18) * S.value }

// ─── Edges (constellation skeleton) ──────────────────────────────────────────
const EDGES_CONFIG: Array<[MoodId, MoodId]> = [
  ["sadness", "fear"],  ["sadness", "calm"],
  ["fear",    "neutral"], ["neutral", "calm"],
  ["calm",    "love"],  ["love", "joy"],
  ["joy",     "energy"], ["energy", "anger"],
  ["anger",   "fear"],  ["love", "sadness"],
  ["love",    "energy"],
]

const edges = computed(() =>
  EDGES_CONFIG.map(([a, b]) => ({
    from: a, to: b,
    isSel: a === props.modelValue || b === props.modelValue,
  }))
)

// ─── Ribbon draw-in animation ─────────────────────────────────────────────────
let ribbonDrawAnim: ReturnType<typeof animate> | null = null

watch(() => props.target, async (newTarget) => {
  if (!newTarget || !props.modelValue || newTarget === props.modelValue) return
  await nextTick(); await nextTick()
  const svgEl   = svgRef.value; if (!svgEl) return
  const pathGlow = svgEl.querySelector(`.ribbon-glow-${uid}`) as SVGPathElement | null
  const pathLine = svgEl.querySelector(`.ribbon-line-${uid}`) as SVGPathElement | null
  if (!pathGlow || !pathLine) return
  pathGlow.setAttribute("stroke-dashoffset", "1")
  pathLine.setAttribute("stroke-dashoffset", "1")
  if (ribbonDrawAnim) ribbonDrawAnim.pause()
  ribbonDrawAnim = animate([pathGlow, pathLine], {
    strokeDashoffset: [1, 0],
    duration: 900, ease: "outExpo",
    delay: (_el: Element, i: number) => i * 60,
  })
})

// ─── Ribbon path ──────────────────────────────────────────────────────────────
const ribbonPath = computed(() => {
  if (!props.target || props.target === props.modelValue) return ""
  const from = points.value[props.modelValue]
  const to   = points.value[props.target]
  if (!from || !to) return ""
  const dx = to.x - from.x, dy = to.y - from.y
  const cx = from.x + dx * 0.5
  const cy = from.y + dy * 0.5 - Math.abs(dy) * 0.28 - 18
  return `M ${from.x} ${from.y} Q ${cx} ${cy} ${to.x} ${to.y}`
})

// ─── Container ────────────────────────────────────────────────────────────────
const containerStyle = computed(() => ({
  position: "relative" as const,
  width: `${props.width}px`,
  height: `${props.height}px`,
}))

// ─── Interaction ──────────────────────────────────────────────────────────────
function select(id: MoodId) {
  if (!props.interactive) return
  if (props.target) {
    emit("update:modelValue", id)
    emit("update:target", undefined)
    moodStore.selectMood(id)
  } else if (id === props.modelValue) {
    // no-op
  } else if (props.modelValue) {
    emit("update:target", id)
    emit("tracePath", { from: props.modelValue, to: id })
  } else {
    emit("update:modelValue", id)
    moodStore.selectMood(id)
  }
}
</script>

<style scoped>
.constellation { position: relative; }

.mood-orb {
  cursor: pointer;
  transition: filter 0.25s ease;
}
.mood-orb:hover { filter: brightness(1.15); }
.mood-orb.selected { cursor: default; }

.mood-label {
  pointer-events: none;
  cursor: default;
}
</style>
