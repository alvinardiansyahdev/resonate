import { defineStore } from "pinia"
import type { Track } from "~/types/track"

let _audio: HTMLAudioElement | null = null

function getAudio(): HTMLAudioElement | null {
  if (!import.meta.client) return null
  if (!_audio) _audio = new Audio()
  return _audio
}

export const usePlayer = defineStore("player", () => {
  const nowPlaying = ref<Track | null>(null)
  const queue = ref<Track[]>([])
  const progress = ref(0)
  const isPlaying = ref(false)
  const isLoading = ref(false)
  const volume = ref(0.7)
  const streamError = ref("")

  let _progressInterval: ReturnType<typeof setInterval> | null = null

  function _startProgressTracking() {
    if (_progressInterval) clearInterval(_progressInterval)
    _progressInterval = setInterval(() => {
      const audio = getAudio()
      if (!audio || !audio.duration) return
      progress.value = audio.currentTime / audio.duration
    }, 500)
  }

  async function play(t: Track) {
    const audio = getAudio()
    nowPlaying.value = t
    isPlaying.value = false
    isLoading.value = true
    streamError.value = ""
    progress.value = 0

    if (audio) {
      audio.pause()
      audio.src = ""
    }

    try {
      const data = await $fetch<{ url: string; mimeType: string }>(`/api/tracks/${t.id}/stream`)
      if (audio) {
        audio.src = data.url
        audio.volume = volume.value
        audio.onended = () => {
          isPlaying.value = false
          next()
        }
        await audio.play()
        isPlaying.value = true
        _startProgressTracking()
      }
    } catch {
      streamError.value = "Stream unavailable"
    } finally {
      isLoading.value = false
    }
  }

  function next() {
    if (queue.value.length > 0) {
      const nextTrack = queue.value.shift()!
      play(nextTrack)
    }
  }

  function previous() {
    const audio = getAudio()
    if (audio) audio.currentTime = 0
    progress.value = 0
  }

  function toggle() {
    const audio = getAudio()
    if (!audio) return
    if (audio.paused) {
      audio.play()
      isPlaying.value = true
      _startProgressTracking()
    } else {
      audio.pause()
      isPlaying.value = false
    }
  }

  function seek(pct: number) {
    const audio = getAudio()
    if (!audio || !audio.duration) return
    audio.currentTime = pct * audio.duration
    progress.value = pct
  }

  function setVolume(v: number) {
    volume.value = v
    const audio = getAudio()
    if (audio) audio.volume = v
  }

  return { nowPlaying, queue, progress, isPlaying, isLoading, streamError, volume, play, next, previous, toggle, seek, setVolume }
})
