<template>
  <main class="lumen-settings">
    <div class="page-content">
      <span class="eyebrow">★ SETTINGS</span>

      <section class="settings-card">
        <h3 class="card-title serif-i">Preferences</h3>

        <div class="setting-row">
          <label class="setting-label">Volume</label>
          <input
            type="range"
            min="0" max="1" step="0.05"
            :value="player.volume"
            @input="player.volume = parseFloat(($event.target as HTMLInputElement).value)"
            class="volume-slider"
          />
        </div>

        <div class="setting-row">
          <label class="setting-label">Reduced motion</label>
          <label class="toggle">
            <input type="checkbox" v-model="reducedMotion" />
            <span class="toggle-track" />
          </label>
        </div>
      </section>

      <p class="version mono">RESONATE · LUMEN · V2.0.0</p>
    </div>

    <PlayerBar />
  </main>
</template>

<script setup lang="ts">
const player = usePlayer()
const reducedMotion = ref(false)

watch(reducedMotion, (val) => {
  document.documentElement.style.setProperty(
    "--reduced-motion",
    val ? "reduce" : "no-preference"
  )
})
</script>

<style scoped>
.lumen-settings {
  position: relative;
  z-index: 1;
  display: flex;
  justify-content: center;
  padding: 40px 24px;
}

.page-content {
  width: 100%;
  max-width: 500px;
}

.settings-card {
  margin-top: 20px;
  padding: 22px;
  border-radius: 16px;
  background: rgba(28, 18, 38, 0.5);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border);
}

.card-title {
  font-size: 20px;
  color: var(--text);
  margin-bottom: 16px;
}

.setting-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid var(--border);
}

.setting-row:last-child {
  border-bottom: none;
}

.setting-label {
  font-size: 14px;
  color: var(--text);
}

.volume-slider {
  width: 120px;
  height: 4px;
  appearance: none;
  background: var(--bg-2);
  border-radius: 2px;
  outline: none;
}

.volume-slider::-webkit-slider-thumb {
  appearance: none;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: var(--accent);
  cursor: pointer;
  box-shadow: 0 0 6px var(--accent);
}

.toggle input {
  display: none;
}

.toggle-track {
  display: block;
  width: 36px;
  height: 20px;
  background: var(--bg-2);
  border-radius: 10px;
  position: relative;
  cursor: pointer;
  transition: background 0.2s;
}

.toggle input:checked + .toggle-track {
  background: var(--accent);
}

.toggle-track::after {
  content: "";
  position: absolute;
  top: 2px;
  left: 2px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--text);
  transition: transform 0.2s;
}

.toggle input:checked + .toggle-track::after {
  transform: translateX(16px);
}

.version {
  margin-top: 32px;
  text-align: center;
  font-size: 10px;
  color: var(--faint);
  letter-spacing: 0.25em;
}
</style>
