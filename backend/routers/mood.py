from fastapi import APIRouter, HTTPException
from backend.models.schemas import Mood, MoodId

router = APIRouter()

MOODS: list[Mood] = [
    Mood(id="sadness", label="Sadness",   color="#60a5fa", hue=220, valence=0.2, arousal=0.2),
    Mood(id="joy",     label="Joy",       color="#facc15", hue=48,  valence=0.8, arousal=0.6),
    Mood(id="anger",   label="Anger",     color="#f87171", hue=0,   valence=0.2, arousal=0.8),
    Mood(id="calm",    label="Calm",      color="#4ade80", hue=142, valence=0.6, arousal=0.2),
    Mood(id="energy",  label="Energy",    color="#fb923c", hue=28,  valence=0.8, arousal=0.8),
    Mood(id="love",    label="Love",      color="#f472b6", hue=330, valence=0.8, arousal=0.6),
    Mood(id="fear",    label="Fear",      color="#a78bfa", hue=262, valence=0.3, arousal=0.7),
    Mood(id="neutral", label="Neutral",   color="#8888a0", hue=240, valence=0.5, arousal=0.5),
]

MOOD_MAP = {m.id: m for m in MOODS}


@router.get("/", response_model=list[Mood])
async def list_moods():
    return MOODS


@router.get("/{mood_id}", response_model=Mood)
async def get_mood(mood_id: str):
    m = MOOD_MAP.get(mood_id)
    if not m:
        raise HTTPException(status_code=404, detail=f"Mood '{mood_id}' not found")
    return m
