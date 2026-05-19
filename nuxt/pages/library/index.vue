<template>
  <main class="lumen-library">
    <div class="page-content">
      <span class="eyebrow">★ JOURNAL</span>
      <p class="section-desc serif-i">Your mood history and past arcs.</p>

      <div class="journal-content" v-if="journal">
        <!-- Mood checkins -->
        <section class="journal-card">
          <div class="card-header">
            <span class="eyebrow">★ MOOD CHECK-INS</span>
            <span class="mono" style="font-size: 9px; color: var(--muted); letter-spacing: 0.2em;">ALL TIME</span>
          </div>
          <div class="counts-grid" v-if="Object.keys(journal.moodCounts).length > 0">
            <div v-for="(count, mood) in journal.moodCounts" :key="mood" class="count-item">
              <span class="count-num serif-i">{{ count }}</span>
              <span class="count-label mono">{{ mood }}</span>
            </div>
          </div>
          <p v-else class="empty-state serif-i">No check-ins yet.</p>
        </section>

        <!-- Past arcs -->
        <section class="journal-card">
          <div class="card-header">
            <span class="eyebrow">★ PAST ARCS</span>
            <span class="serif-i" style="font-size: 12px; color: var(--gold);">view all →</span>
          </div>
          <div v-if="journal.arcs.length > 0" class="arcs-list">
            <div v-for="arcItem in journal.arcs" :key="arcItem.id" class="arc-entry">
              <NuxtLink :to="`/library/${arcItem.id}`" class="arc-link">
                <div class="arc-moods">
                  <span class="arc-label serif-i">{{ arcItem.label || `${arcItem.from_mood} → ${arcItem.to_mood}` }}</span>
                  <div class="arc-path" v-if="arcItem.from_mood">
                    <span class="path-dot" :style="{ background: moodColor(arcItem.from_mood) }" />
                    <span class="mono path-label">{{ arcItem.from_mood.toUpperCase() }}</span>
                    <span class="path-line" :style="{ background: `linear-gradient(90deg, ${moodColor(arcItem.from_mood)}, ${moodColor(arcItem.to_mood)})` }" />
                    <span class="mono path-label">{{ arcItem.to_mood.toUpperCase() }}</span>
                    <span class="path-dot" :style="{ background: moodColor(arcItem.to_mood) }" />
                  </div>
                </div>
                <span class="arc-date mono">{{ formatDate(arcItem.createdAt) }}</span>
              </NuxtLink>
            </div>
          </div>
          <p v-else class="empty-state serif-i">No arcs yet. Start your journey on the Discover page.</p>
        </section>
      </div>
    </div>

    <PlayerBar />
  </main>
</template>

<script setup lang="ts">
const { data: journal } = await useFetch("/api/journal")

const MOOD_COLORS: Record<string, string> = {
  sadness: "#60a5fa", joy: "#facc15", anger: "#f87171",
  calm: "#4ade80", energy: "#fb923c", love: "#f472b6",
  fear: "#a78bfa", neutral: "#8888a0",
}

function moodColor(id: string) {
  return MOOD_COLORS[id] ?? "var(--accent)"
}

function formatDate(iso: string): string {
  const d = new Date(iso)
  const days = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
  const months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
  return `${days[d.getDay()]} · ${months[d.getMonth()]} ${d.getDate()}`
}
</script>

<style scoped>
.lumen-library {
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

.section-desc {
  font-size: 14px;
  color: var(--muted);
  margin-top: 6px;
  margin-bottom: 24px;
}

.journal-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.journal-card {
  padding: 22px;
  border-radius: 16px;
  background: rgba(28, 18, 38, 0.5);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border);
}

.card-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 14px;
}

.counts-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.count-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  background: rgba(28, 18, 38, 0.6);
  border-radius: 999px;
  border: 1px solid var(--border);
}

.count-num {
  font-size: 20px;
  color: var(--gold);
  line-height: 1;
}

.count-label {
  font-size: 10px;
  color: var(--muted);
  letter-spacing: 0.15em;
  text-transform: uppercase;
}

.arcs-list {
  display: flex;
  flex-direction: column;
}

.arc-entry {
  padding: 12px 0;
  border-bottom: 1px solid var(--border);
}

.arc-entry:last-child {
  border-bottom: none;
}

.arc-link {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: var(--text);
  text-decoration: none;
  transition: color 0.2s;
}

.arc-link:hover {
  color: var(--accent);
}

.arc-label {
  font-size: 18px;
  line-height: 1.15;
}

.arc-path {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 4px;
}

.path-dot {
  width: 6px;
  height: 6px;
  border-radius: 999px;
  flex-shrink: 0;
}

.path-label {
  font-size: 8px;
  color: var(--muted);
  letter-spacing: 0.15em;
}

.path-line {
  width: 30px;
  height: 1px;
}

.arc-date {
  font-size: 9px;
  color: var(--faint);
  letter-spacing: 0.15em;
  flex-shrink: 0;
}

.empty-state {
  font-size: 14px;
  color: var(--faint);
  padding: 12px 0;
}
</style>
