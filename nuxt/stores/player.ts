import { defineStore } from "pinia"
import type { Track } from "~/types/track"

export const usePlayer = defineStore("player", () => {
  const nowPlaying = ref<Track | null>(null)
  const queue = ref<Track[]>([])
  const progress = ref(0)
  const isPlaying = ref(false)
  const volume = ref(0.7)

  function play(t: Track) {
    nowPlaying.value = t
    isPlaying.value = true
    progress.value = 0
  }

  function next() {
    if (queue.value.length > 0) {
      const nextTrack = queue.value.shift()!
      play(nextTrack)
    }
  }

  function previous() {
    progress.value = 0
  }

  function toggle() {
    isPlaying.value = !isPlaying.value
  }

  return { nowPlaying, queue, progress, isPlaying, volume, play, next, previous, toggle }
})
