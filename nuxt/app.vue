<template>
  <div id="resonate-app">
    <!-- Three.js full-page star field (WebGL, behind everything) -->
    <AmbientStarField />

    <!-- Atmospheric mood glow blobs (on top of stars, behind content) -->
    <div class="lumen-bg">
      <div class="bg-blob bg-magenta" />
      <div class="bg-blob bg-mood" />
    </div>

    <AppTopbar />
    <NuxtPage />
  </div>
</template>

<script setup lang="ts">
useMoodTheme()
</script>

<style>
html {
  background: var(--bg-0);
  color: var(--text);
}

body {
  overflow-x: hidden;
}

#resonate-app {
  position: relative;
  min-height: 100vh;
}

/* Deep background gradient */
#resonate-app::before {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: -1;
  background: radial-gradient(ellipse at 30% 20%, #2a1640 0%, var(--bg-1) 50%, var(--bg-0) 100%);
}

/* Atmospheric blobs float above starfield, behind content */
.lumen-bg {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 1;
  overflow: hidden;
}

.bg-blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  transition: background 0.6s ease;
}

.bg-magenta {
  right: -10%;
  top: -15%;
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(240, 171, 252, 0.18) 0%, transparent 70%);
}

.bg-mood {
  left: -15%;
  bottom: -20%;
  width: 700px;
  height: 700px;
  background: radial-gradient(circle, var(--mood-glow) 0%, transparent 65%);
}

/* Page content sits above blobs */
.lumen-topbar,
main,
[class^="lumen-"] {
  position: relative;
  z-index: 2;
}
</style>
