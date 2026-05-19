export type MoodId =
  | "sadness"
  | "joy"
  | "anger"
  | "calm"
  | "energy"
  | "love"
  | "fear"
  | "neutral"

export interface Mood {
  id: MoodId
  label: string
  color: string
  hue: number
  valence: number
  arousal: number
}
