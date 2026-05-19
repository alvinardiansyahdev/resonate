import math
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from backend.models.schemas import Arc, ArcRequest, ArcShape, ArcWaypoint, PlaylistRequest, Track
from backend.routers.songs import build_arc_tracks
from backend.routers.mood import MOOD_MAP

router = APIRouter()

ARC_SHAPES: list[ArcShape] = ["lift", "release", "ignite", "stay"]


@router.get("/shapes")
async def list_shapes():
    return [
        {"id": "lift",    "label": "Lift gradually",     "desc": "A slow climb from melancholy to calm."},
        {"id": "release", "label": "Release and reset",  "desc": "Catharsis, then quiet."},
        {"id": "ignite",  "label": "Build energy",       "desc": "From still to alive."},
        {"id": "stay",    "label": "Stay where I am",    "desc": "Hold this feeling. Lean in."},
    ]


@router.post("/", response_model=Arc)
async def create_arc(req: ArcRequest):
    steps = 7
    waypoint_pcts = [0, 17, 33, 50, 67, 83, 100]
    waypoint_labels = [
        "start", "early", "rising", "midpoint",
        "deepening", "approaching", "arrive"
    ]
    mood_ids = [
        "sadness", "calm", "neutral", "neutral",
        "joy", "joy", "calm"
    ]
    waypoints = [
        ArcWaypoint(mood=mood_ids[i], label=waypoint_labels[i], pct=waypoint_pcts[i])
        for i in range(steps)
    ]

    tracks = build_arc_tracks(req.from_mood, req.to_mood, steps)

    arc = Arc(
        id=str(uuid.uuid4())[:8],
        from_mood=req.from_mood,
        to_mood=req.to_mood,
        shape=req.shape,
        tracks=tracks,
        waypoints=waypoints,
        createdAt=datetime.now(timezone.utc).isoformat(),
    )
    return arc


@router.post("/resolve-seed")
async def resolve_seed_endpoint(body: dict):
    from backend.services.playlist_generator import resolve_seed
    seed_query = body.get("seed_query", "").strip()
    if not seed_query:
        raise HTTPException(status_code=422, detail="seed_query is required")
    seed = await resolve_seed(seed_query)
    if not seed:
        raise HTTPException(status_code=404, detail="Song not found")
    return {"title": seed["title"], "artist": seed["uploader"], "id": seed["id"]}


_WAYPOINT_LABELS = ["start", "early", "rising", "midpoint", "deepening", "approaching", "arrive"]


@router.post("/playlist", response_model=Arc)
async def create_playlist(req: PlaylistRequest):
    from backend.services.playlist_generator import generate_playlist

    try:
        result = await generate_playlist(
            seed_query=req.seed_query,
            from_mood=req.from_mood,
            to_mood=req.to_mood,
            steps=req.steps,
            shape=req.shape,
            similarity_weight=req.similarity_weight,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    trajectory = result["trajectory"]
    waypoints = []
    for i, pt in enumerate(trajectory):
        mood_tag = min(
            MOOD_MAP.items(),
            key=lambda x: math.sqrt((x[1].valence - pt["valence"]) ** 2 + (x[1].arousal - pt["arousal"]) ** 2),
        )[0]
        waypoints.append(ArcWaypoint(
            mood=mood_tag,
            label=_WAYPOINT_LABELS[i] if i < len(_WAYPOINT_LABELS) else f"step {i + 1}",
            pct=round(i / max(len(trajectory) - 1, 1) * 100),
        ))

    tracks = [Track(**{k: v for k, v in t.items() if k != "thumbnail"}) for t in result["tracks"]]

    seed = result.get("seed", {})
    return Arc(
        id=str(uuid.uuid4())[:8],
        from_mood=req.from_mood,
        to_mood=req.to_mood,
        shape=req.shape,
        tracks=tracks,
        waypoints=waypoints,
        createdAt=datetime.now(timezone.utc).isoformat(),
        seedTitle=seed.get("title"),
        seedArtist=seed.get("artist"),
    )
