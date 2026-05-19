import { defineStore } from "pinia"
import type { Arc, ArcShape } from "~/types/arc"
import type { MoodId } from "~/types/mood"

export const useArc = defineStore("arc", () => {
  const active = ref<Arc | null>(null)
  const waypoints = computed(() => active.value?.waypoints ?? [])
  const chapterIdx = ref(0)

  async function begin(
    from: MoodId,
    to: MoodId,
    shape: ArcShape,
    opts?: { seedQuery?: string; similarityWeight?: number; steps?: number },
  ) {
    const arc = opts?.seedQuery?.trim()
      ? await $fetch<Arc>("/api/arcs/playlist", {
          method: "POST",
          body: {
            seed_query: opts.seedQuery.trim(),
            from_mood: from,
            to_mood: to,
            shape,
            steps: opts.steps ?? 7,
            similarity_weight: opts.similarityWeight ?? 0.7,
          },
        })
      : await $fetch<Arc>("/api/arcs", {
          method: "POST",
          body: { from_mood: from, to_mood: to, shape },
        })
    active.value = arc
    chapterIdx.value = 0
    const player = usePlayer()
    if (arc.tracks.length > 0) {
      player.play(arc.tracks[0]!)
    }
  }

  return { active, waypoints, chapterIdx, begin }
})
