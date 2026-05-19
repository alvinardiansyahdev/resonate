<template>
  <main class="lumen-arc-detail">
    <div class="page-content">
      <NuxtLink to="/library" class="back-link serif-i">← Back to journal</NuxtLink>

      <div v-if="arc" class="arc-header">
        <span class="eyebrow">★ ARC DETAIL</span>
        <h1 class="arc-path serif-i">{{ arc.label || `${arc.from_mood} → ${arc.to_mood}` }}</h1>
        <p class="arc-shape mono">{{ arc.shape }} journey</p>
      </div>

      <section class="tracks-section" v-if="arc?.tracks?.length">
        <span class="eyebrow">★ TRACKS</span>
        <div class="tracks-list">
          <div v-for="(track, i) in arc.tracks" :key="track.id" class="track-row">
            <span class="track-idx mono">{{ String(i + 1).padStart(2, "0") }}</span>
            <div class="track-orb" :style="{ background: `radial-gradient(circle at 30% 30%, #fff, ${moodColor(track.moodTag)} 50%, ${moodColor(track.moodTag)}60)` }" />
            <div class="track-info">
              <span class="track-title serif-i">{{ track.title }}</span>
              <span class="track-artist">{{ track.artist }}</span>
            </div>
            <span class="track-mood mono">{{ track.moodTag }}</span>
          </div>
        </div>
      </section>

      <p v-else class="empty-state serif-i">No track data available for this arc.</p>
    </div>

    <PlayerBar />
  </main>
</template>

<script setup lang="ts">
import type { Arc } from "~/types/arc"

const route = useRoute()
const { data: journal } = await useFetch("/api/journal")

const arc = computed(() => {
  if (!journal.value) return null
  return journal.value.arcs.find((a: Arc) => a.id === route.params.arcId) ?? null
})

const MOOD_COLORS: Record<string, string> = {
  sadness: "#60a5fa", joy: "#facc15", anger: "#f87171",
  calm: "#4ade80", energy: "#fb923c", love: "#f472b6",
  fear: "#a78bfa", neutral: "#8888a0",
}

function moodColor(id: string) {
  return MOOD_COLORS[id] ?? "var(--accent)"
}
</script>

<style scoped>
.lumen-arc-detail {
  position: relative;
  z-index: 1;
  display: flex;
  justify-content: center;
  padding: 40px 24px;
}

.page-content {
  width: 100%;
  max-width: 640px;
}

.back-link {
  display: inline-block;
  font-size: 14px;
  color: var(--accent);
  margin-bottom: 20px;
  text-decoration: none;
}

.back-link:hover {
  color: var(--accent-2);
}

.arc-header {
  margin-bottom: 24px;
}

.arc-path {
  font-size: 28px;
  color: var(--text);
  margin-top: 8px;
}

.arc-shape {
  font-size: 11px;
  color: var(--muted);
  margin-top: 4px;
  letter-spacing: 0.15em;
  text-transform: capitalize;
}

.tracks-section {
  margin-top: 8px;
}

.tracks-list {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.track-row {
  display: grid;
  grid-template-columns: 28px 36px 1fr auto;
  gap: 12px;
  align-items: center;
  padding: 10px 12px;
  border-radius: 10px;
  background: rgba(28, 18, 38, 0.4);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--border);
}

.track-idx {
  font-size: 11px;
  color: var(--faint);
  letter-spacing: 0.1em;
  text-align: right;
}

.track-orb {
  width: 32px;
  height: 32px;
  border-radius: 8px;
}

.track-info {
  display: flex;
  flex-direction: column;
}

.track-title {
  font-size: 16px;
  line-height: 1.15;
  color: var(--text);
}

.track-artist {
  font-size: 10px;
  color: var(--muted);
  margin-top: 1px;
}

.track-mood {
  font-size: 9px;
  color: var(--muted);
  padding: 3px 10px;
  border-radius: 999px;
  background: rgba(28, 18, 38, 0.6);
  border: 1px solid var(--border);
  letter-spacing: 0.15em;
  text-transform: uppercase;
}

.empty-state {
  font-size: 14px;
  color: var(--faint);
  margin-top: 20px;
}
</style>
