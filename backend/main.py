import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from backend.routers import mood, trajectory, songs, journal

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


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "resonate", "version": "2.0.0"}


def main():
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=False)


if __name__ == "__main__":
    main()
