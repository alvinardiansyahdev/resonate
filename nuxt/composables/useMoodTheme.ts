import type { MoodId } from "~/types/mood"
import { animate } from "animejs"

const MOOD_COLORS: Record<MoodId, string> = {
  sadness: "#60a5fa",
  joy: "#facc15",
  anger: "#f87171",
  calm: "#4ade80",
  energy: "#fb923c",
  love: "#f472b6",
  fear: "#a78bfa",
  neutral: "#8888a0",
}

const MOOD_LIGHT: Record<MoodId, string> = {
  sadness: "#a5c9ff",
  joy: "#fde68a",
  anger: "#fca5a5",
  calm: "#86efac",
  energy: "#fdba74",
  love: "#f9a8d4",
  fear: "#c4b5fd",
  neutral: "#c0c0d8",
}

// Proxy object that anime.js mutates when tweening between colors
const colorProxy = { accent: "#c084fc", accent2: "#f0abfc" }
let colorAnim: ReturnType<typeof animate> | null = null

export function useMoodTheme() {
  const mood = useMood()

  const theme = computed(() => {
    const id = mood.current ?? "love"
    const color = MOOD_COLORS[id]
    return {
      accent: color,
      accent2: MOOD_LIGHT[id],
      glow: `${color}30`,
    }
  })

  watch(theme, (newTheme) => {
    if (import.meta.server) return
    const s = document.documentElement.style

    // Sync proxy to current CSS variable values so the tween starts from them
    colorProxy.accent  = s.getPropertyValue("--accent").trim()  || colorProxy.accent
    colorProxy.accent2 = s.getPropertyValue("--accent-2").trim() || colorProxy.accent2

    // Cancel any in-flight animation
    if (colorAnim) colorAnim.pause()

    colorAnim = animate(colorProxy, {
      accent:  newTheme.accent,
      accent2: newTheme.accent2,
      duration: 600,
      ease: "outQuart",
      onUpdate() {
        s.setProperty("--accent",     colorProxy.accent)
        s.setProperty("--accent-2",   colorProxy.accent2)
        s.setProperty("--mood-glow",  `${colorProxy.accent}28`)
      },
    })
  }, { immediate: false })

  // Initialize on first call (no animation, just set)
  onMounted(() => {
    if (import.meta.server) return
    const s = document.documentElement.style
    const id = mood.current ?? "love"
    const color = MOOD_COLORS[id]
    colorProxy.accent  = color
    colorProxy.accent2 = MOOD_LIGHT[id]
    s.setProperty("--accent",    color)
    s.setProperty("--accent-2",  MOOD_LIGHT[id])
    s.setProperty("--mood-glow", `${color}28`)
  })

  return theme
}
