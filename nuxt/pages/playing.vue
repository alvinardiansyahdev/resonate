<template>
  <main class="lumen-playing" v-if="player.nowPlaying">
    <!-- LEFT: Editorial chapter -->
    <div class="left-panel">
      <div class="chapter-bg-num serif-i">04</div>

      <div class="chapter-content">
        <span class="eyebrow">★ CHAPTER IV — ARRIVAL</span>

        <h1 class="track-title serif">
          <span class="italic">{{ player.nowPlaying.title }}.</span>
        </h1>

        <div class="track-meta">
          <span class="artist-name">{{ player.nowPlaying.artist }}</span>
          <span class="mono album-name">— from {{ player.nowPlaying.album }}, 2014</span>
        </div>

        <!-- Lyric pull-quote -->
        <div class="lyric-block">
          <div class="lyric-bar" />
          <span class="eyebrow">verse 2 · 02:14</span>
          <div class="lyric-text serif-i">"{{ lyric }}"</div>
        </div>

        <!-- Glass waveform card -->
        <div class="waveform-card">
          <div class="waveform-header">
            <span class="eyebrow-muted">waveform · 02:14 / {{ formatTime(duration) }}</span>
            <span class="eyebrow-muted">{{ keySig }}</span>
          </div>
          <WaveformBars
            :count="60"
            :width="480"
            :height="52"
            :color="accent"
            :split="0.42"
          />
          <div class="waveform-time">
            <span class="time-mono">00:00</span>
            <span class="time-accent">● {{ progressStr }}</span>
            <span class="time-mono">{{ formatTime(duration) }}</span>
          </div>
        </div>
      </div>

      <!-- Bottom glass control bar -->
      <div class="control-bar">
        <!-- Shuffle -->
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="16 3 21 3 21 8"/>
          <line x1="4" y1="20" x2="21" y2="3"/>
          <polyline points="21 16 21 21 16 21"/>
          <line x1="15" y1="15" x2="21" y2="21"/>
          <line x1="4" y1="4" x2="9" y2="9"/>
        </svg>
        <!-- Prev -->
        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><polygon points="5,4 15,12 5,20"/><rect x="17" y="4" width="2" height="16"/></svg>

        <button class="play-btn-lg" @click="player.toggle()">
          <svg v-if="player.isPlaying" width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>
          <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><polygon points="8,5 19,12 8,19"/></svg>
        </button>

        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><polygon points="19,20 9,12 19,4"/><rect x="5" y="4" width="2" height="16"/></svg>
        <div class="ctrl-spacer" />
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>
        <div style="width:1px;height:18px;background:var(--border)" />
        <span class="mono" style="font-size:9px;color:var(--faint);letter-spacing:0.2em;">SPACE · ← →</span>
      </div>
    </div>

    <!-- RIGHT: Artwork + journey + up next -->
    <div class="right-panel">
      <!-- Artwork glass orb -->
      <div class="orb-wrapper">
        <ArtworkOrb :size="200" :color="accent" />
      </div>

      <!-- Journey card -->
      <div class="journey-card" v-if="arc.active">
        <div class="journey-card-header">
          <span class="eyebrow">★ JOURNEY · {{ fromLabel }} → {{ toLabel }}</span>
          <span class="mono" style="font-size:9px;color:var(--muted);letter-spacing:0.2em;">
            {{ chapterRoman }} / {{ totalChapters }}
          </span>
        </div>
        <TrajectoryRibbon
          :from-mood="arcOrigin"
          :to-mood="arcDestination"
          :width="420"
          :height="88"
        />
        <ChapterDots
          :waypoints="chapterWaypoints"
          :current="arc.chapterIdx"
        />
      </div>

      <!-- Up next -->
      <div class="up-next">
        <span class="eyebrow">★ COMING UP</span>
        <div class="up-next-list">
          <div v-for="(q, i) in upcoming" :key="i" class="up-next-item">
            <div class="up-chapter">
              <span class="eyebrow-muted">CH.</span>
              <span class="serif-i up-chap-num">{{ q.chap }}</span>
            </div>
            <div class="up-orb" :style="{ background: `radial-gradient(circle at 30% 30%, #fff, ${q.color} 50%, ${q.color}60)`, boxShadow: `0 0 12px ${q.color}40` }" />
            <div class="up-info">
              <div class="serif-i up-title">{{ q.title }}</div>
              <div class="up-meta">{{ q.artist }} · {{ q.mood }}</div>
            </div>
            <span class="mono up-dur">{{ q.dur }}</span>
          </div>
        </div>
      </div>
    </div>
  </main>

  <!-- Empty state -->
  <main class="lumen-playing" v-else>
    <div class="empty-state">
      <h2 class="serif-i" style="font-size:28px;color:var(--muted);">No track playing</h2>
      <p class="mono" style="font-size:12px;color:var(--faint);margin-top:8px;">Start an arc from the Discover page.</p>
    </div>
  </main>
</template>

<script setup lang="ts">
const player = usePlayer()
const arc = useArc()
const theme = useMoodTheme()
const accent = computed(() => theme.value.accent)

const moodLabels: Record<string, string> = {
  sadness: "Sadness", joy: "Joy", anger: "Anger", calm: "Calm",
  energy: "Energy", love: "Love", fear: "Fear", neutral: "Neutral",
}

const MOOD_COLORS: Record<string, string> = {
  sadness: "#60a5fa", joy: "#facc15", anger: "#f87171",
  calm: "#4ade80", energy: "#fb923c", love: "#f472b6",
  fear: "#a78bfa", neutral: "#8888a0",
}

const lyric = "You taught yourself to live inside of your own dark, and proudly stayed unchanged from when you'd first awoke."
const keySig = "F♯ MIN · 76 BPM"

const duration = computed(() => player.nowPlaying?.duration ?? 288)
const progressStr = computed(() => formatTime(player.progress * duration.value))

const chapterRoman = computed(() => {
  const idx = arc.chapterIdx ?? 0
  const map = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]
  return map[idx] ?? String(idx + 1)
})

const totalChapters = "VII"
const fromLabel = computed(() => moodLabels[arc.active?.from_mood] ?? "")
const toLabel = computed(() => moodLabels[arc.active?.to_mood] ?? "")
const arcOrigin = computed(() => arc.active?.from_mood ?? "love")
const arcDestination = computed(() => arc.active?.to_mood ?? "joy")

const chapterWaypoints = computed(() => {
  return arc.waypoints?.length ? arc.waypoints : Array(7).fill({})
})

const upcoming = computed(() => [
  { title: "Light", artist: "Sleeping at Last", dur: "4:51", chap: "V", mood: "calm", color: MOOD_COLORS.calm },
  { title: "A Sky Full of Stars", artist: "Coldplay", dur: "4:28", chap: "VI", mood: "joy", color: MOOD_COLORS.joy },
  { title: "Eyes", artist: "Kaskobi", dur: "3:18", chap: "VII", mood: "energy", color: MOOD_COLORS.energy },
])

function formatTime(seconds: number) {
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, "0")}`
}
</script>

<style scoped>
.lumen-playing {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: 1fr 1.05fr;
  min-height: calc(100vh - 70px);
}

.left-panel {
  padding: 32px 40px;
  position: relative;
  overflow: hidden;
}

.chapter-bg-num {
  position: absolute;
  right: 30px;
  top: 0;
  font-size: 240px;
  line-height: 0.8;
  color: rgba(232, 200, 135, 0.04);
  pointer-events: none;
}

.chapter-content {
  position: relative;
}

.track-title {
  font-size: 72px;
  line-height: 0.93;
  margin-top: 10px;
}

.track-meta {
  margin-top: 14px;
  display: flex;
  align-items: baseline;
  gap: 14px;
}

.artist-name {
  font-size: 20px;
  color: var(--text);
}

.album-name {
  font-size: 11px;
  color: var(--muted);
  letter-spacing: 0.15em;
}

.lyric-block {
  margin-top: 28px;
  padding: 20px 0 20px 24px;
  max-width: 480px;
  position: relative;
  border-left: 2px solid var(--gold);
}

.lyric-bar {
  position: absolute;
  left: -1px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: linear-gradient(180deg, var(--gold), var(--accent));
  box-shadow: 0 0 8px color-mix(in srgb, var(--gold) 25%, transparent);
}

.lyric-text {
  font-size: 24px;
  line-height: 1.3;
  margin-top: 10px;
  color: var(--text-hi);
}

.waveform-card {
  margin-top: 28px;
  padding: 16px 20px;
  border-radius: 16px;
  background: rgba(28, 18, 38, 0.55);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border);
  box-shadow: 0 20px 40px -12px rgba(0, 0, 0, 0.4);
}

.waveform-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.waveform-time {
  display: flex;
  justify-content: space-between;
  margin-top: 4px;
}

.time-mono {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--faint);
}

.time-accent {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--accent);
}

/* Bottom control bar */
.control-bar {
  position: absolute;
  left: 40px;
  right: 40px;
  bottom: 24px;
  padding: 12px 20px;
  border-radius: 16px;
  background: rgba(13, 6, 18, 0.75);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid var(--border);
  display: flex;
  align-items: center;
  gap: 16px;
  color: var(--muted);
}

.control-bar svg {
  cursor: pointer;
  transition: color 0.2s;
}

.control-bar svg:hover {
  color: var(--text);
}

.play-btn-lg {
  width: 42px;
  height: 42px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--accent), var(--accent-2));
  color: #1a0a26;
  box-shadow: 0 8px 20px -6px color-mix(in srgb, var(--accent) 50%, transparent);
  transition: transform 0.15s;
}

.play-btn-lg:hover {
  transform: scale(1.05);
}

.ctrl-spacer {
  flex: 1;
}

/* RIGHT PANEL */
.right-panel {
  border-left: 1px solid var(--border);
  padding: 32px 40px;
  display: flex;
  flex-direction: column;
  background: radial-gradient(ellipse at 50% 25%, color-mix(in srgb, var(--accent) 19%, transparent) 0%, transparent 60%);
}

.orb-wrapper {
  display: flex;
  justify-content: center;
}

.journey-card {
  margin-top: 20px;
  padding: 16px 18px;
  border-radius: 14px;
  background: rgba(28, 18, 38, 0.55);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border);
}

.journey-card-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 10px;
}

.up-next {
  margin-top: 22px;
  flex: 1;
}

.up-next-list {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.up-next-item {
  display: grid;
  grid-template-columns: 32px 32px 1fr auto;
  gap: 10px;
  align-items: center;
  padding: 8px 10px;
  border-radius: 10px;
  background: rgba(28, 18, 38, 0.4);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--border);
}

.up-chapter {
  text-align: center;
}

.up-chap-num {
  font-size: 16px;
  color: var(--gold);
  line-height: 1;
}

.up-orb {
  width: 28px;
  height: 28px;
  border-radius: 6px;
}

.up-title {
  font-size: 16px;
  line-height: 1.15;
}

.up-meta {
  font-size: 10px;
  color: var(--muted);
  margin-top: 1px;
}

.up-dur {
  font-size: 10px;
  color: var(--muted);
}

.empty-state {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
}
</style>
