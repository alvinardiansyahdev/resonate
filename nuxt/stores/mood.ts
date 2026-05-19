import { defineStore } from "pinia"
import type { MoodId } from "~/types/mood"

export const useMood = defineStore("mood", () => {
  const current = ref<MoodId | null>(null)
  const suggested = ref<MoodId | null>(null)
  const recent = ref<MoodId[]>([])

  async function selectMood(id: MoodId) {
    current.value = id
    recent.value = [id, ...recent.value].slice(0, 12)
  }

  return { current, suggested, recent, selectMood }
})
