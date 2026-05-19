import math
import os
import random
import httpx
from fastapi import APIRouter, HTTPException
from backend.models.schemas import Track, MoodId
from backend.routers.mood import MOOD_MAP

PIPED_BASE = os.getenv("PIPED_BASE_URL", "http://piped:8080")

router = APIRouter()

TRACKS: list[Track] = [
    Track(id="t1",  title="Holocene",                artist="Bon Iver",             album="Bon Iver, Bon Iver",                      duration=336,  streamUrl="", moodTag="calm",   valence=0.55, arousal=0.25),
    Track(id="t2",  title="A Sky Full of Stars",     artist="Coldplay",             album="Ghost Stories",                            duration=268,  streamUrl="", moodTag="joy",    valence=0.75, arousal=0.65),
    Track(id="t3",  title="Motion Picture Soundtrack",artist="Radiohead",           album="Kid A",                                     duration=421,  streamUrl="", moodTag="sadness", valence=0.15, arousal=0.15),
    Track(id="t4",  title="Re: Stacks",              artist="Bon Iver",             album="For Emma, Forever Ago",                    duration=401,  streamUrl="", moodTag="sadness", valence=0.20, arousal=0.20),
    Track(id="t5",  title="The Night We Met",        artist="Lord Huron",           album="Strange Trails",                            duration=268,  streamUrl="", moodTag="fear",   valence=0.30, arousal=0.35),
    Track(id="t6",  title="Light",                   artist="Sleeping at Last",     album="Atlas: Year One",                          duration=291,  streamUrl="", moodTag="calm",   valence=0.60, arousal=0.20),
    Track(id="t7",  title="Saturn",                  artist="Sleeping at Last",     album="Atlas: Space",                              duration=288,  streamUrl="", moodTag="love",   valence=0.75, arousal=0.45),
    Track(id="t8",  title="Daylight",                artist="David Kushner",        album="Daylight",                                  duration=212,  streamUrl="", moodTag="fear",   valence=0.25, arousal=0.50),
    Track(id="t9",  title="Cornfield Chase",         artist="Hans Zimmer",          album="Interstellar (OST)",                        duration=126,  streamUrl="", moodTag="neutral", valence=0.50, arousal=0.30),
    Track(id="t10", title="Eyes",                    artist="Kaskobi",              album="Singles",                                   duration=198,  streamUrl="", moodTag="energy", valence=0.80, arousal=0.75),
    Track(id="t11", title="Rosyln",                  artist="Bon Iver & St. Vincent",album="Twilight: New Moon (OST)",                duration=280,  streamUrl="", moodTag="love",   valence=0.70, arousal=0.35),
    Track(id="t12", title="Intro",                   artist="The xx",               album="xx",                                        duration=127,  streamUrl="", moodTag="neutral", valence=0.45, arousal=0.20),
    Track(id="t13", title="Bloom",                   artist="Beach House",          album="Depression Cherry",                         duration=237,  streamUrl="", moodTag="calm",   valence=0.60, arousal=0.30),
    Track(id="t14", title="The less I know the better",artist="Tame Impala",       album="Currents",                                  duration=336,  streamUrl="", moodTag="energy", valence=0.70, arousal=0.70),
    Track(id="t15", title="Nude",                    artist="Radiohead",            album="In Rainbows",                               duration=255,  streamUrl="", moodTag="sadness", valence=0.25, arousal=0.25),
    Track(id="t16", title="Breathe",                 artist="Telepopmusik",         album="Genesis",                                   duration=275,  streamUrl="", moodTag="calm",   valence=0.50, arousal=0.15),
    Track(id="t17", title="Mr. Brightside",          artist="The Killers",          album="Hot Fuss",                                  duration=222,  streamUrl="", moodTag="energy", valence=0.60, arousal=0.80),
    Track(id="t18", title="Fix You",                 artist="Coldplay",             album="X&Y",                                       duration=295,  streamUrl="", moodTag="love",   valence=0.70, arousal=0.40),
    Track(id="t19", title="Everybody Wants To Rule The World",artist="Tears for Fears",album="Songs from the Big Chair",              duration=282,  streamUrl="", moodTag="joy",    valence=0.65, arousal=0.55),
    Track(id="t20", title="Weightless",              artist="Marconi Union",        album="Weightless (Ambient Transmissions vol. 2)", duration=480,  streamUrl="", moodTag="calm",   valence=0.50, arousal=0.10),
    Track(id="t21", title="Not Allowed",             artist="TV Girl",              album="Who Really Cares",                         duration=187,  streamUrl="", moodTag="anger",  valence=0.25, arousal=0.70),
    Track(id="t22", title="Lovers Rock",             artist="TV Girl",              album="French Exit",                               duration=207,  streamUrl="", moodTag="love",   valence=0.65, arousal=0.35),
    Track(id="t23", title="Apocalypse",              artist="Cigarettes After Sex", album="Cigarettes After Sex",                      duration=290,  streamUrl="", moodTag="sadness", valence=0.20, arousal=0.25),
    Track(id="t24", title="K.",                      artist="Cigarettes After Sex", album="Cigarettes After Sex",                      duration=319,  streamUrl="", moodTag="love",   valence=0.65, arousal=0.30),
    Track(id="t25", title="Glimpse of Us",           artist="Joji",                 album="SMITHEREENS",                               duration=228,  streamUrl="", moodTag="sadness", valence=0.25, arousal=0.30),
    Track(id="t26", title="Runaway",                 artist="Kanye West",           album="My Beautiful Dark Twisted Fantasy",         duration=538,  streamUrl="", moodTag="fear",   valence=0.30, arousal=0.45),
    Track(id="t27", title="Heat Waves",              artist="Glass Animals",        album="Dreamland",                                 duration=238,  streamUrl="", moodTag="joy",    valence=0.70, arousal=0.45),
    Track(id="t28", title="505",                     artist="Arctic Monkeys",       album="Favourite Worst Nightmare",                 duration=253,  streamUrl="", moodTag="anger",  valence=0.30, arousal=0.65),
    Track(id="t29", title="Evergreen",               artist="Richy Mitch & The Coal Miners",album="RMP",                          duration=114,  streamUrl="", moodTag="calm",   valence=0.55, arousal=0.15),
    Track(id="t30", title="champagne problems",      artist="Taylor Swift",         album="evermore",                                  duration=255,  streamUrl="", moodTag="sadness", valence=0.20, arousal=0.20),
]


def sigmoid(t: float, k: float = 6) -> float:
    x = (t - 0.5) * k
    return 1 / (1 + math.exp(-x))


def find_closest_tracks(valence: float, arousal: float, n: int = 3) -> list[Track]:
    scored = []
    for t in TRACKS:
        dist = math.sqrt((t.valence - valence) ** 2 + (t.arousal - arousal) ** 2)
        scored.append((dist, t))
    scored.sort(key=lambda x: x[0])
    return [t for _, t in scored[:n]]


def build_arc_tracks(from_mood: str, to_mood: str, steps: int) -> list[Track]:
    f = MOOD_MAP[from_mood]
    t = MOOD_MAP[to_mood]
    tracks: list[Track] = []
    used_ids: set[str] = set()
    for i in range(steps):
        p = i / (steps - 1) if steps > 1 else 0
        s = sigmoid(p, 6)
        v = f.valence + (t.valence - f.valence) * s
        a = f.arousal + (t.arousal - f.arousal) * s
        candidates = find_closest_tracks(v, a, 5)
        picked = None
        for c in candidates:
            if c.id not in used_ids:
                picked = c
                used_ids.add(c.id)
                break
        if not picked:
            picked = candidates[0]
            used_ids.add(picked.id)
        tracks.append(picked)
    return tracks


@router.get("/{track_id}/stream")
async def get_stream_url(track_id: str):
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(f"{PIPED_BASE}/streams/{track_id}")
    if r.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Piped returned {r.status_code}")
    data = r.json()
    audio_streams = data.get("audioStreams", [])
    if not audio_streams:
        raise HTTPException(status_code=404, detail="No audio streams found")
    best = max(audio_streams, key=lambda s: s.get("bitrate", 0))
    return {"url": best["url"], "mimeType": best.get("mimeType", "audio/webm"), "duration": data.get("duration", 0)}


@router.get("/{track_id}", response_model=Track)
async def get_track(track_id: str):
    for t in TRACKS:
        if t.id == track_id:
            return t
    raise HTTPException(status_code=404, detail=f"Track '{track_id}' not found")
