import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Query
from backend.models.schemas import JournalEntry, CheckinRequest, CheckinResponse, JournalResponse, Arc, Track

router = APIRouter()

_journal: list[JournalEntry] = []
_arcs: list[Arc] = []


@router.get("", response_model=JournalResponse)
async def get_journal(range: str = Query("week", regex="^(week|month|quarter)$")):
    return JournalResponse(
        arcs=_arcs,
        moodCounts=_count_moods(),
    )


@router.post("/checkin", response_model=CheckinResponse)
async def checkin(req: CheckinRequest):
    entry = JournalEntry(
        id=str(uuid.uuid4())[:8],
        mood=req.mood,
        note=req.note,
        createdAt=datetime.now(timezone.utc).isoformat(),
    )
    _journal.append(entry)
    return CheckinResponse(ok=True)


def add_arc(arc: Arc):
    _arcs.append(arc)


def _count_moods() -> dict:
    counts: dict[str, int] = {}
    for entry in _journal:
        counts[entry.mood] = counts.get(entry.mood, 0) + 1
    return counts
