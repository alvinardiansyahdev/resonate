<template>
  <main class="lumen-discover">
    <!-- LEFT: Constellation field -->
    <div class="left-panel">
      <div class="panel-header">
        <span class="eyebrow">★ THE FIELD</span>
        <span class="eyebrow-muted">{{ dateStr }}</span>
      </div>

      <h1 class="hero-title serif">
        What pulls you<br /><span class="italic" style="color: var(--gold)">tonight?</span>
      </h1>

      <p class="hero-desc serif-i">
        Trace a line between two stars. Each path is a slow walk we'll soundtrack —
        ambient, beat-by-beat, until you arrive somewhere new.
      </p>

      <div class="field-wrapper">
        <MoodConstellationField
          v-model="selectedMood"
          v-model:target="targetMood"
          :width="600"
          :height="380"
          :interactive="true"
          @trace-path="onTracePath"
        />
      </div>

      <!-- Bottom glass strip -->
      <div class="glass-strip" v-if="selectedMood">
        <div style="display:flex;align-items:center;gap:10px;">
          <div class="mood-dot" :style="{ background: moodColor, boxShadow: `0 0 12px ${moodColor}` }" />
          <div>
            <span class="eyebrow-muted">CURRENT</span>
            <div class="strip-mood serif-i">{{ fromLabel }}</div>
          </div>
        </div>
        <div class="strip-divider" />
        <div>
          <span class="eyebrow-muted">COORDINATE</span>
          <div class="mono strip-coord">{{ coordStr }}</div>
        </div>
        <div class="strip-spacer" />
        <div v-if="!targetMood" class="strip-hint serif-i">
          Or <span style="color:var(--gold);border-bottom:1px solid var(--gold)">blend two feelings</span> →
        </div>
      </div>
    </div>

    <!-- RIGHT: Trajectory column -->
    <div class="right-panel">
      <div class="panel-header">
        <span class="eyebrow">★ THE JOURNEY</span>
        <span class="mono" style="font-size:9px;color:var(--muted);letter-spacing:0.2em;">IV ARCS</span>
      </div>

      <h2 class="journey-title serif">
        Where shall we<br /><span class="italic">take this?</span>
      </h2>

      <!-- Selected preview -->
      <div class="preview-card" v-if="targetMood && selectedMood !== targetMood">
        <span class="eyebrow" style="color:var(--accent);">selected · {{ fromLabel.toLowerCase() }} → {{ toLabel.toLowerCase() }}</span>
        <TrajectoryRibbon
          :from-mood="selectedMood"
          :to-mood="targetMood"
          :width="340"
          :height="80"
        />
        <div class="preview-labels">
          <span class="mono" style="font-size:9px;color:var(--muted);letter-spacing:0.2em;">{{ fromLabel.toUpperCase() }} · NOW</span>
          <span class="mono" style="font-size:9px;color:var(--muted);letter-spacing:0.2em;">{{ toLabel.toUpperCase() }} · ≈ 28 MIN</span>
        </div>
      </div>

      <!-- Seed song input -->
      <div class="seed-section">
        <span class="eyebrow" style="color:var(--accent);">★ SEED SONG</span>
        <p class="seed-hint serif-i">Drop a YouTube link or type a title — we'll find acoustically similar songs.</p>
        <div class="seed-input-row">
          <input
            v-model="seedQuery"
            class="seed-input mono"
            placeholder="e.g. Koi Iro Ni Somaru"
            :disabled="isResolving || isGenerating"
            @keydown.enter="resolveSeed"
            @input="resolvedSeed = null"
          />
          <button v-if="isResolving" class="seed-resolving" disabled>⟳</button>
          <button v-else-if="seedQuery && !resolvedSeed" class="seed-go mono" @click="resolveSeed">→</button>
          <button v-else-if="seedQuery" class="seed-clear" @click="clearSeed">✕</button>
        </div>

        <!-- Resolved seed confirmation -->
        <div v-if="resolvedSeed" class="seed-confirmed">
          <span class="eyebrow-muted">FOUND</span>
          <span class="seed-confirmed-title serif-i">{{ resolvedSeed.title }}</span>
          <span class="eyebrow-muted" style="color:var(--faint)">{{ resolvedSeed.artist }}</span>
        </div>
        <div v-if="seedError" class="seed-err mono">{{ seedError }}</div>

        <div v-if="resolvedSeed" class="sim-row">
          <span class="eyebrow-muted">FAMILIAR</span>
          <input
            v-model.number="similarityWeight"
            type="range" min="0.3" max="0.95" step="0.05"
            class="sim-slider"
          />
          <span class="eyebrow-muted">MOOD</span>
          <span class="sim-value mono">{{ Math.round(similarityWeight * 100) }}%</span>
        </div>
      </div>

      <TrajectoryCard
        v-for="(shape, i) in shapes"
        :key="shape.id"
        :label="shape.label"
        :desc="shape.desc"
        :shape="shape.id"
        :from-label="fromLabel"
        :to-label="toLabel"
        :num="i + 1"
        :selected="shape.id === selectedShape"
        @select="selectedShape = shape.id as ArcShape"
      />

      <button
        class="begin-btn serif-i"
        :class="{ loading: isGenerating, 'needs-seed': seedQuery && !resolvedSeed && !isResolving }"
        :disabled="isGenerating || (!!seedQuery && !resolvedSeed)"
        @click="startArc(selectedShape)"
      >
        <span>{{ isGenerating ? 'building playlist…' : 'begin the journey' }}</span>
        <span class="mono" style="font-size:11px;letter-spacing:0.3em;opacity:0.7;">{{ isGenerating ? '⟳' : '↪ ENTER' }}</span>
      </button>
      <p v-if="generateError" class="gen-error mono">{{ generateError }}</p>
    </div>

    <PlayerBar />
  </main>
</template>

<script setup lang="ts">
import type { ArcShape } from "~/types/arc"
import type { MoodId } from "~/types/mood"

const moodStore = useMood()
const arcStore = useArc()
const router = useRouter()

const selectedMood = ref<MoodId>(moodStore.current ?? "neutral")
const targetMood = ref<MoodId | undefined>(undefined)
const seedQuery = ref("")
const resolvedSeed = ref<{ title: string; artist: string; query: string } | null>(null)
const similarityWeight = ref(0.7)
const selectedShape = ref<ArcShape>("lift")
const isResolving = ref(false)
const isGenerating = ref(false)
const generateError = ref("")
const seedError = ref("")

const FALLBACK_SHAPES = [
  { id: "stay",    label: "Stay where I am",  desc: "Hold this feeling. Lean in." },
  { id: "lift",    label: "Lift gradually",   desc: "A slow climb from melancholy to calm." },
  { id: "release", label: "Release and reset", desc: "Catharsis, then quiet." },
  { id: "ignite",  label: "Build energy",     desc: "From still to alive." },
]
const { data: shapesData } = await useFetch<typeof FALLBACK_SHAPES>("/api/arcs/shapes", {
  default: () => FALLBACK_SHAPES,
})
const shapes = computed(() => shapesData.value ?? FALLBACK_SHAPES)

const dateStr = computed(() => {
  const d = new Date()
  const days = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
  const months = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
  return `tonight · ${days[d.getDay()]} · ${months[d.getMonth()]} ${d.getDate()}`
})

const moodColors: Record<string, string> = {
  sadness: "#60a5fa", joy: "#facc15", anger: "#f87171",
  calm: "#4ade80", energy: "#fb923c", love: "#f472b6",
  fear: "#a78bfa", neutral: "#8888a0",
}

const moodLabels: Record<string, string> = {
  sadness: "Sadness", joy: "Joy", anger: "Anger", calm: "Calm",
  energy: "Energy", love: "Love", fear: "Fear", neutral: "Neutral",
}

const MOOD_COORDS: Record<string, string> = {
  sadness: "220° · ❄ · −0.62", joy: "48° · ☀ · +0.85",
  anger: "0° · 🔥 · −0.48", calm: "142° · 🌊 · +0.12",
  energy: "28° · ⚡ · +0.72", love: "330° · ❤ · +0.55",
  fear: "262° · 🌫 · −0.35", neutral: "240° · ◐ · 0.00",
}

const fromLabel = computed(() => moodLabels[selectedMood.value] ?? "")
const toLabel = computed(() => targetMood.value ? moodLabels[targetMood.value] ?? "" : "")
const coordStr = computed(() => MOOD_COORDS[selectedMood.value] ?? "240° · ◐ · 0.00")
const moodColor = computed(() => moodColors[selectedMood.value] ?? "#c084fc")

function onTracePath(payload: { from: MoodId; to: MoodId }) {
  selectedMood.value = payload.from
  targetMood.value = payload.to
  moodStore.selectMood(payload.from)
}

async function resolveSeed() {
  const q = seedQuery.value.trim()
  if (!q) return
  seedError.value = ""
  resolvedSeed.value = null
  isResolving.value = true
  try {
    const res = await $fetch<{ title: string; artist: string }>("/api/arcs/resolve-seed", {
      method: "POST",
      body: { seed_query: q },
    })
    resolvedSeed.value = { title: res.title, artist: res.artist, query: q }
  } catch {
    seedError.value = "Song not found — try a different title or paste a YouTube URL."
  } finally {
    isResolving.value = false
  }
}

function clearSeed() {
  seedQuery.value = ""
  resolvedSeed.value = null
  seedError.value = ""
}

async function startArc(shape: string) {
  generateError.value = ""
  isGenerating.value = true
  try {
    await arcStore.begin(
      selectedMood.value,
      targetMood.value ?? selectedMood.value,
      shape as ArcShape,
      resolvedSeed.value
        ? { seedQuery: resolvedSeed.value.query, similarityWeight: similarityWeight.value }
        : undefined,
    )
    router.push("/playing")
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e)
    generateError.value = "Could not build playlist — try again."
    console.error(msg)
  } finally {
    isGenerating.value = false
  }
}
</script>

<style scoped>
.lumen-discover {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: 1fr 420px;
  min-height: calc(100vh - 70px);
}

.left-panel {
  padding: 32px 40px;
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
}

.hero-title {
  font-size: 56px;
  line-height: 0.98;
  margin-top: 14px;
  font-weight: 400;
}

.hero-desc {
  font-size: 15px;
  color: var(--muted);
  margin-top: 14px;
  max-width: 500px;
  line-height: 1.6;
}

.field-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 12px;
}

.glass-strip {
  padding: 12px 18px;
  border-radius: 14px;
  background: rgba(28, 18, 38, 0.55);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border);
  display: flex;
  align-items: center;
  gap: 24px;
}

.mood-dot {
  width: 12px;
  height: 12px;
  border-radius: 999px;
  flex-shrink: 0;
}

.strip-mood {
  font-size: 20px;
  line-height: 1;
  margin-top: 2px;
}

.strip-coord {
  font-size: 13px;
  margin-top: 4px;
}

.strip-divider {
  width: 1px;
  align-self: stretch;
  background: var(--border);
}

.strip-spacer {
  flex: 1;
}

.strip-hint {
  font-size: 14px;
  color: var(--muted);
}

/* RIGHT PANEL */
.right-panel {
  background: linear-gradient(180deg, rgba(28, 18, 38, 0.4), rgba(13, 6, 18, 0.6));
  border-left: 1px solid var(--border);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  padding: 28px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.journey-title {
  font-size: 28px;
  line-height: 1.1;
}

.preview-card {
  padding: 14px;
  border-radius: 14px;
  background: rgba(192, 132, 252, 0.06);
  border: 1px solid color-mix(in srgb, var(--accent) 15%, transparent);
}

.preview-labels {
  display: flex;
  justify-content: space-between;
}

/* Seed song section */
.seed-section {
  padding: 14px;
  border-radius: 14px;
  background: rgba(28, 18, 38, 0.5);
  border: 1px solid var(--border);
}

.seed-hint {
  font-size: 12px;
  color: var(--muted);
  margin: 4px 0 10px;
  line-height: 1.4;
}

.seed-input-row {
  position: relative;
  display: flex;
  align-items: center;
}

.seed-input {
  width: 100%;
  padding: 9px 36px 9px 12px;
  border-radius: 9px;
  background: rgba(13, 6, 18, 0.6);
  border: 1px solid var(--border);
  color: var(--text);
  font-size: 12px;
  letter-spacing: 0.04em;
  outline: none;
  transition: border-color 0.2s;
}

.seed-input:focus {
  border-color: var(--accent);
}

.seed-input::placeholder {
  color: var(--faint);
}

.seed-clear {
  position: absolute;
  right: 10px;
  background: none;
  border: none;
  color: var(--muted);
  font-size: 11px;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.seed-go {
  position: absolute;
  right: 8px;
  background: var(--accent);
  border: none;
  color: #1a0a26;
  font-size: 13px;
  font-weight: 700;
  width: 22px;
  height: 22px;
  border-radius: 5px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  transition: opacity 0.15s;
}

.seed-go:hover { opacity: 0.85; }

.seed-resolving {
  position: absolute;
  right: 10px;
  background: none;
  border: none;
  color: var(--accent);
  font-size: 13px;
  animation: spin 0.8s linear infinite;
  padding: 0;
  line-height: 1;
}

@keyframes spin { to { transform: rotate(360deg); } }

.seed-confirmed {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-top: 8px;
  padding: 7px 10px;
  border-radius: 8px;
  background: color-mix(in srgb, var(--accent) 8%, transparent);
  border: 1px solid color-mix(in srgb, var(--accent) 20%, transparent);
}

.seed-confirmed-title {
  font-size: 14px;
  color: var(--text-hi);
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.seed-err {
  font-size: 10px;
  color: #f87171;
  margin-top: 6px;
  letter-spacing: 0.05em;
}

.begin-btn.needs-seed {
  opacity: 0.4;
  cursor: not-allowed;
}

.sim-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
}

.sim-slider {
  flex: 1;
  accent-color: var(--accent);
  height: 3px;
  cursor: pointer;
}

.sim-value {
  font-size: 10px;
  color: var(--accent);
  width: 32px;
  text-align: right;
}

.begin-btn {
  margin-top: auto;
  padding: 14px 18px;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--accent), var(--accent-2));
  color: #1a0a26;
  border: none;
  font-size: 20px;
  font-style: italic;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 12px 32px -10px color-mix(in srgb, var(--accent) 50%, transparent);
  transition: transform 0.15s, opacity 0.15s;
}

.begin-btn:hover:not(:disabled) {
  transform: scale(1.02);
}

.begin-btn.loading,
.begin-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.gen-error {
  font-size: 10px;
  color: #f87171;
  text-align: center;
  margin-top: -4px;
  letter-spacing: 0.05em;
}
</style>
