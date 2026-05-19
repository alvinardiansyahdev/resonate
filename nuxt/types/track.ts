import type { MoodId } from "./mood"

export interface Track {
  id: string
  title: string
  artist: string
  album: string
  duration: number
  streamUrl: string
  moodTag: MoodId
  valence: number
  arousal: number
}
