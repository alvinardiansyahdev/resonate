import type { MoodId } from "./mood"
import type { Track } from "./track"

export type ArcShape = "lift" | "release" | "ignite" | "stay"

export interface ArcWaypoint {
  mood: MoodId
  label: string
  pct: number
}

export interface Arc {
  id: string
  from_mood: MoodId
  to_mood: MoodId
  shape: ArcShape
  tracks: Track[]
  waypoints: ArcWaypoint[]
  createdAt: string
  seedTitle?: string
  seedArtist?: string
}
