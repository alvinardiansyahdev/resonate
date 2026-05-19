from pydantic import BaseModel
from typing import List, Optional, Literal


MoodId = Literal[
    "sadness", "joy", "anger", "calm",
    "energy", "love", "fear", "neutral"
]


class Mood(BaseModel):
    id: str
    label: str
    color: str
    hue: int
    valence: float
    arousal: float


class Track(BaseModel):
    id: str
    title: str
    artist: str
    album: str
    duration: int
    streamUrl: str
    moodTag: str
    valence: float
    arousal: float


ArcShape = Literal["lift", "release", "ignite", "stay"]


class ArcWaypoint(BaseModel):
    mood: str
    label: str
    pct: float


class Arc(BaseModel):
    id: str
    from_mood: str
    to_mood: str
    shape: str
    tracks: List[Track]
    waypoints: List[ArcWaypoint]
    createdAt: str


class ArcRequest(BaseModel):
    from_mood: str
    to_mood: str
    shape: ArcShape = "lift"


class JournalEntry(BaseModel):
    id: str
    mood: str
    note: Optional[str] = None
    createdAt: str


class PlaylistRequest(BaseModel):
    seed_query: str
    from_mood: str
    to_mood: str
    shape: str = "sigmoid"
    steps: int = 7
    similarity_weight: float = 0.7


class CheckinRequest(BaseModel):
    mood: str
    note: Optional[str] = None


class CheckinResponse(BaseModel):
    ok: bool


class JournalResponse(BaseModel):
    arcs: List[Arc]
    moodCounts: dict
