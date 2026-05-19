<template>
  <div v-if="player.nowPlaying" class="player-bar">
    <ArtworkOrb :size="48" :color="accent" />

    <div class="track-info">
      <h4 class="track-title serif-i">{{ player.nowPlaying.title }}</h4>
      <p class="track-artist">{{ player.nowPlaying.artist }}</p>
    </div>

    <div class="player-controls">
      <button class="ctrl-btn" @click="player.previous()" aria-label="Previous">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><polygon points="19,20 9,12 19,4"/><rect x="5" y="4" width="2" height="16"/></svg>
      </button>

      <button class="play-btn" @click="player.toggle()" aria-label="Play/Pause" :disabled="player.isLoading">
        <svg v-if="player.isLoading" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spin"><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/></svg>
        <svg v-else-if="player.isPlaying" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>
        <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><polygon points="8,5 19,12 8,19"/></svg>
      </button>

      <button class="ctrl-btn" @click="player.next()" aria-label="Next">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><polygon points="5,4 15,12 5,20"/><rect x="17" y="4" width="2" height="16"/></svg>
      </button>
    </div>

    <div class="progress-area">
      <div class="progress-track">
        <div class="progress-fill" :style="{ width: `${player.progress * 100}%` }" />
        <div class="progress-thumb" :style="{ left: `${player.progress * 100}%` }" />
      </div>
      <div class="progress-time">
        <span class="mono time">{{ formatTime(player.progress * (player.nowPlaying.duration || 180)) }}</span>
        <span class="mono time">{{ formatTime(player.nowPlaying.duration || 180) }}</span>
      </div>
    </div>

    <div class="extras">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>
    </div>

    <span v-if="player.streamError" class="stream-error mono">{{ player.streamError }}</span>
    <span v-else class="shortcuts-hint mono">SPACE · ← →</span>
  </div>
</template>

<script setup lang="ts">
const player = usePlayer()
const theme = useMoodTheme()
const accent = computed(() => theme.value.accent)

function formatTime(seconds: number) {
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, "0")}`
}
</script>

<style scoped>
.player-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 14px 22px;
  background: rgba(13, 6, 18, 0.75);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-top: 1px solid var(--border);
  display: flex;
  align-items: center;
  gap: 18px;
  z-index: 50;
}

.track-info {
  min-width: 0;
  max-width: 200px;
}

.track-title {
  font-size: 0.9rem;
  color: var(--text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.track-artist {
  font-size: 0.7rem;
  color: var(--muted);
}

.player-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.ctrl-btn {
  width: 32px;
  height: 32px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text);
  transition: background 0.2s;
}

.ctrl-btn:hover {
  background: rgba(255, 255, 255, 0.06);
}

.play-btn {
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

.play-btn:hover {
  transform: scale(1.05);
}

.progress-area {
  flex: 1;
  max-width: 200px;
}

.progress-track {
  position: relative;
  height: 2px;
  border-radius: 999px;
  background: var(--border);
}

.progress-fill {
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, var(--accent), var(--accent-2));
  box-shadow: 0 0 6px var(--accent);
  transition: width 0.25s linear;
}

.progress-thumb {
  position: absolute;
  top: 50%;
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: #fff;
  box-shadow: 0 0 8px var(--accent);
  transform: translate(-50%, -50%);
  opacity: 0;
  transition: opacity 0.2s;
}

.progress-track:hover .progress-thumb {
  opacity: 1;
}

.progress-time {
  display: flex;
  justify-content: space-between;
  margin-top: 2px;
}

.time {
  font-size: 9px;
  color: var(--faint);
}

.extras {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--muted);
}

.shortcuts-hint {
  font-size: 9px;
  color: var(--faint);
  letter-spacing: 0.2em;
}

.stream-error {
  font-size: 9px;
  color: #f87171;
  letter-spacing: 0.1em;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
.spin {
  animation: spin 0.8s linear infinite;
}
</style>
