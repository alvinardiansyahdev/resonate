<template>
  <header class="lumen-topbar">
    <div class="topbar-left">
      <div class="logo-orb">
        <div class="logo-orb-inner" />
        <div class="logo-orb-glow" />
      </div>
      <NuxtLink to="/" class="logo-link">
        <span class="serif-i logo-text">resonate</span>
      </NuxtLink>
      <span class="mono lumen-badge">★ LUMEN</span>
    </div>

    <nav class="topbar-nav">
      <NuxtLink
        v-for="item in navItems" :key="item.to"
        :to="item.to"
        class="nav-pill"
        :class="{ active: isActive(item.to) }"
      >
        {{ item.label }}
      </NuxtLink>
    </nav>

    <div class="topbar-right">
      <div class="avatar-orb" />
    </div>
  </header>
</template>

<script setup lang="ts">
const route = useRoute()

const navItems = [
  { to: "/", label: "Discover" },
  { to: "/playing", label: "Now Playing" },
  { to: "/library", label: "Journal" },
  { to: "/settings", label: "Settings" },
]

function isActive(path: string) {
  return route.path === path || route.path.startsWith(path + "/")
}
</script>

<style scoped>
.lumen-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 40px;
  border-bottom: 1px solid var(--border);
  background: rgba(13, 6, 18, 0.4);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  position: sticky;
  top: 0;
  z-index: 50;
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logo-orb {
  position: relative;
  width: 22px;
  height: 22px;
  flex-shrink: 0;
}

.logo-orb-inner {
  position: absolute;
  inset: 4px;
  border-radius: 50%;
  background: radial-gradient(circle at 35% 35%, #fff, var(--accent) 60%, color-mix(in srgb, var(--accent) 50%, transparent));
}

.logo-orb-glow {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  box-shadow: 0 0 10px var(--accent);
}

.logo-link {
  text-decoration: none;
  color: inherit;
}

.logo-text {
  font-size: 26px;
  letter-spacing: -0.01em;
  color: var(--text);
}

.lumen-badge {
  font-size: 9px;
  color: var(--faint);
  letter-spacing: 0.25em;
}

.topbar-nav {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: rgba(13, 6, 18, 0.6);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.nav-pill {
  padding: 6px 18px;
  border-radius: 999px;
  font-size: 12px;
  color: var(--muted);
  text-decoration: none;
  text-transform: capitalize;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.nav-pill.active {
  font-family: var(--font-serif);
  font-style: italic;
  font-size: 14px;
  background: linear-gradient(135deg, color-mix(in srgb, var(--accent) 16%, transparent), color-mix(in srgb, var(--gold) 9%, transparent));
  color: var(--text-hi);
  border-color: color-mix(in srgb, var(--accent) 25%, transparent);
  text-transform: none;
}

.nav-pill:hover:not(.active) {
  color: var(--text);
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.avatar-orb {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent), #f472b6);
  box-shadow: 0 0 12px color-mix(in srgb, var(--accent) 31%, transparent);
}
</style>
