import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import httpx
import uvicorn

from backend.routers import mood, trajectory, songs, journal, webhook

PIPED_BASE = os.getenv("PIPED_BASE_URL", "http://piped:8080")

app = FastAPI(
    title="Resonate API",
    description="Mood-driven emotional music curation engine",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(mood.router, prefix="/api/moods", tags=["mood"])
app.include_router(songs.router, prefix="/api/tracks", tags=["tracks"])
app.include_router(trajectory.router, prefix="/api/arcs", tags=["arcs"])
app.include_router(journal.router, prefix="/api/journal", tags=["journal"])
app.include_router(webhook.router, prefix="/api/deploy", tags=["deploy"])


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "resonate", "version": "2.0.0"}


@app.get("/search")
async def piped_search(q: str = Query(...), filter: str = Query("videos")):
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(f"{PIPED_BASE}/search", params={"q": q, "filter": filter})
    if r.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Piped search returned {r.status_code}")
    return r.json()


@app.get("/api/stream")
async def get_stream_by_id(id: str = Query(...)):
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    import yt_dlp

    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(f"{PIPED_BASE}/streams/{id}")

    if r.status_code == 200:
        data = r.json()
        audio_streams = data.get("audioStreams", [])
        if audio_streams:
            audio_streams.sort(key=lambda s: s.get("bitrate", 0), reverse=True)
            return {
                "title": data.get("title", ""),
                "uploader": data.get("uploader", ""),
                "duration": data.get("duration", 0),
                "thumbnail": data.get("thumbnailUrl", ""),
                "url": audio_streams[0]["url"],
            }

    # Piped failed — fall back to yt-dlp
    def _ytdlp():
        with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True, "format": "bestaudio/best"}) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={id}", download=False)
        if not info:
            raise ValueError("yt-dlp returned no info")
        url = info.get("url") or next((f["url"] for f in info.get("formats", []) if f.get("acodec") != "none" and f.get("url")), None)
        if not url:
            raise ValueError("No audio URL")
        return {"title": info.get("title", ""), "uploader": info.get("uploader", ""), "duration": info.get("duration", 0), "thumbnail": info.get("thumbnail", ""), "url": url}

    try:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(ThreadPoolExecutor(max_workers=2), _ytdlp)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


_player_dir = Path(__file__).parent.parent / "player"

@app.get("/player")
async def serve_player():
    return FileResponse(_player_dir / "index.html")


def main():
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=False)


if __name__ == "__main__":
    main()
