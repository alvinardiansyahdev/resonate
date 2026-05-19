import httpx
import math
import os
import re
from typing import Optional

PIPED_BASE = os.getenv("PIPED_BASE_URL", "http://piped:8080")

MOOD_VA: dict[str, tuple[float, float]] = {
    "sadness": (0.2, 0.2),
    "joy":     (0.8, 0.6),
    "anger":   (0.2, 0.8),
    "calm":    (0.6, 0.2),
    "energy":  (0.8, 0.8),
    "love":    (0.8, 0.6),
    "fear":    (0.3, 0.7),
    "neutral": (0.5, 0.5),
}

# Delta VA from neutral (0.5, 0.45) when keyword found in text
_KW: dict[str, tuple[float, float]] = {
    "sad":          (-0.30, -0.20), "sadness":   (-0.30, -0.20),
    "melancholy":   (-0.25, -0.15), "cry":       (-0.30, -0.10),
    "tears":        (-0.25, -0.10), "heartbreak":(-0.30, -0.05),
    "happy":        ( 0.30,  0.15), "happiness": ( 0.30,  0.15),
    "joy":          ( 0.30,  0.15), "dance":     ( 0.20,  0.30),
    "party":        ( 0.25,  0.35), "club":      ( 0.20,  0.30),
    "angry":        (-0.30,  0.35), "anger":     (-0.30,  0.35),
    "rage":         (-0.35,  0.40), "hate":      (-0.30,  0.30),
    "calm":         ( 0.10, -0.30), "ambient":   ( 0.05, -0.35),
    "sleep":        ( 0.00, -0.40), "meditat":   ( 0.05, -0.35),
    "peaceful":     ( 0.15, -0.30), "quiet":     ( 0.05, -0.30),
    "love":         ( 0.30,  0.05), "romance":   ( 0.25,  0.00),
    "tender":       ( 0.20, -0.10), "energy":    ( 0.25,  0.35),
    "hype":         ( 0.25,  0.40), "chill":     ( 0.10, -0.25),
    "relax":        ( 0.10, -0.30), "lofi":      ( 0.05, -0.25),
    "fear":         (-0.20,  0.30), "horror":    (-0.25,  0.35),
    "dark":         (-0.15,  0.15), "epic":      ( 0.15,  0.30),
    "uplifting":    ( 0.25,  0.15), "beautiful": ( 0.20,  0.00),
    "nostalgia":    (-0.05, -0.10), "bittersweet":(-0.05, 0.00),
    "inspirational":( 0.20,  0.20),
}


def _sigmoid(t: float, k: float = 8.0) -> float:
    return 1.0 / (1.0 + math.exp(-(t - 0.5) * k))


def build_trajectory(
    from_mood: str, to_mood: str, steps: int, shape: str
) -> list[tuple[float, float]]:
    fv, fa = MOOD_VA.get(from_mood, (0.5, 0.5))
    tv, ta = MOOD_VA.get(to_mood, (0.5, 0.5))
    result = []
    for i in range(steps):
        t = i / (steps - 1) if steps > 1 else 0.0
        if shape == "sigmoid":
            p = _sigmoid(t)
        elif shape == "flat":
            p = 0.5
        else:
            p = t
        result.append((fv + (tv - fv) * p, fa + (ta - fa) * p))
    return result


def estimate_va(title: str, uploader: str = "") -> tuple[float, float]:
    text = (title + " " + uploader).lower()
    dv = da = 0.0
    hits = 0
    for kw, (dv_, da_) in _KW.items():
        if kw in text:
            dv += dv_
            da += da_
            hits += 1
    base_v, base_a = 0.50, 0.45
    if hits:
        return (
            max(0.0, min(1.0, base_v + dv / hits)),
            max(0.0, min(1.0, base_a + da / hits)),
        )
    return base_v, base_a


def _extract_vid_id(s: str) -> Optional[str]:
    m = re.search(r"(?:youtube\.com/watch\?v=|youtu\.be/|/watch\?v=)([a-zA-Z0-9_-]{11})", s)
    return m.group(1) if m else None


async def resolve_seed(query: str, piped_base: str = PIPED_BASE) -> Optional[dict]:
    vid_id = _extract_vid_id(query)
    async with httpx.AsyncClient(timeout=12) as client:
        if vid_id:
            r = await client.get(f"{piped_base}/streams/{vid_id}")
            if r.status_code == 200:
                d = r.json()
                return {
                    "id": vid_id,
                    "title": d.get("title", ""),
                    "uploader": d.get("uploader", ""),
                    "duration": d.get("duration", 0),
                }
        else:
            r = await client.get(f"{piped_base}/search", params={"q": query, "filter": "music_songs"})
            if r.status_code == 200:
                items = r.json().get("items", [])
                if items:
                    item = items[0]
                    url = item.get("url", "")
                    vid = _extract_vid_id(url)
                    if not vid:
                        vid = url.replace("/watch?v=", "").lstrip("/")
                    return {
                        "id": vid,
                        "title": item.get("title", ""),
                        "uploader": item.get("uploaderName", ""),
                        "duration": item.get("duration", 0),
                    }
    return None


async def get_related(video_id: str, piped_base: str = PIPED_BASE) -> list[dict]:
    async with httpx.AsyncClient(timeout=12) as client:
        r = await client.get(f"{piped_base}/streams/{video_id}")
        if r.status_code != 200:
            return []
        related = r.json().get("relatedStreams", [])
        out = []
        for item in related:
            url = item.get("url", "")
            vid = _extract_vid_id(url)
            if not vid:
                continue
            out.append({
                "id": vid,
                "title": item.get("title", ""),
                "uploader": item.get("uploaderName", ""),
                "duration": item.get("duration", 0),
                "thumbnail": item.get("thumbnail", ""),
            })
        return out


async def generate_playlist(
    seed_query: str,
    from_mood: str,
    to_mood: str,
    steps: int = 7,
    shape: str = "sigmoid",
    similarity_weight: float = 0.7,
    piped_base: str = PIPED_BASE,
) -> dict:
    seed = await resolve_seed(seed_query, piped_base)
    if not seed:
        raise ValueError(f"Could not resolve seed song: {seed_query!r}")

    candidates = await get_related(seed["id"], piped_base)
    trajectory = build_trajectory(from_mood, to_mood, steps, shape)
    emotion_weight = 1.0 - similarity_weight

    used: set[str] = {seed["id"]}
    tracks = []

    for step_idx, (tv, ta) in enumerate(trajectory):
        best = None
        best_score: Optional[float] = None

        for rank, c in enumerate(candidates):
            if c["id"] in used:
                continue
            cv, ca = estimate_va(c["title"], c["uploader"])
            emo_dist = math.sqrt((cv - tv) ** 2 + (ca - ta) ** 2)
            # Lower rank = more acoustically similar (YouTube surfaces these first)
            sim_rank = rank / max(len(candidates) - 1, 1)
            score = emotion_weight * emo_dist + similarity_weight * sim_rank
            if best_score is None or score < best_score:
                best_score = score
                best = (c, cv, ca)

        if best is None:
            for c in candidates:
                if c["id"] not in used:
                    best = (c, *estimate_va(c["title"], c["uploader"]))
                    break

        if best:
            c, cv, ca = best
            used.add(c["id"])
            mood_tag = min(
                MOOD_VA.items(),
                key=lambda x: math.sqrt((x[1][0] - cv) ** 2 + (x[1][1] - ca) ** 2),
            )[0]
            tracks.append({
                "id": c["id"],
                "title": c["title"],
                "artist": c["uploader"],
                "album": "",
                "duration": c["duration"],
                "streamUrl": f"https://www.youtube.com/watch?v={c['id']}",
                "moodTag": mood_tag,
                "valence": round(cv, 3),
                "arousal": round(ca, 3),
                "thumbnail": c.get("thumbnail", ""),
            })

    return {
        "seed": {
            "id": seed["id"],
            "title": seed["title"],
            "artist": seed["uploader"],
        },
        "tracks": tracks,
        "trajectory": [
            {"valence": round(v, 3), "arousal": round(a, 3)}
            for v, a in trajectory
        ],
    }
