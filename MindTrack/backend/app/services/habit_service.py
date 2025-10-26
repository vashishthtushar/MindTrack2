from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional, Iterator, Tuple

# /c:/Users/Sweta.Singh/Downloads/project/tts/new/backend/app/services/habit_service.py

# Adjust import to match your project's model location
try:
    from app.models import DailyHabitEntry
except Exception:
    # Fallback stub model for type hints / dev-time safety
    class DailyHabitEntry:
        id: int
        user_id: int
        habit_name: str
        date: date
        status: str
        notes: Optional[str]
        timestamp: datetime
        created_at: datetime
        updated_at: datetime

        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)


# Helper: convert model -> dict (Derived Summary / entry representation)
def _entry_to_dict(entry: DailyHabitEntry) -> Dict[str, Any]:
    return {
        "id": getattr(entry, "id", None),
        "user_id": getattr(entry, "user_id", None),
        "habit_name": getattr(entry, "habit_name", None),
        "date": getattr(entry, "date", None),
        "status": getattr(entry, "status", None),
        "notes": getattr(entry, "notes", None),
        "timestamp": getattr(entry, "timestamp", None),
        "created_at": getattr(entry, "created_at", None),
        "updated_at": getattr(entry, "updated_at", None),
    }


# Internal helper: inclusive daterange generator
def _daterange(start: date, end: date) -> Iterator[date]:
    if start is None or end is None:
        return iter(())
    if start > end:
        return iter(())
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


# Internal helper: calculates current and max streaks from sorted date list (ascending)
def _calculate_streak(dates_list: List[date]) -> Tuple[int, int]:
    """
    dates_list: sorted unique list of date objects in ascending order representing 'done' dates.
    Returns (current_streak, max_streak).
    """
    if not dates_list:
        return 0, 0

    max_streak = 1
    curr_streak = 1

    # Compute max streak by scanning ascending
    for i in range(1, len(dates_list)):
        if dates_list[i] == dates_list[i - 1] + timedelta(days=1):
            curr_streak += 1
        else:
            if curr_streak > max_streak:
                max_streak = curr_streak
            curr_streak = 1
    if curr_streak > max_streak:
        max_streak = curr_streak

    # Compute current streak: walk backwards from last date
    current_streak = 1
    for i in range(len(dates_list) - 1, 0, -1):
        if dates_list[i] == dates_list[i - 1] + timedelta(days=1):
            current_streak += 1
        else:
            break

    return current_streak, max_streak


# Core service functions

def create_habit_entry(db, entry_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates and inserts new DailyHabitEntry.
    Prevent duplicate (user_id, date, habit_name) via upsert logic:
      - If an entry exists for (user_id, date, habit_name) update it with provided fields.
      - Otherwise create a new record.
    Returns the saved entry as a dict.
    """
    required = ("user_id", "habit_name", "date")
    for k in required:
        if k not in entry_data:
            raise ValueError(f"Missing required field: {k}")

    user_id = entry_data["user_id"]
    habit_name = entry_data["habit_name"]
    entry_date = entry_data["date"]
    if isinstance(entry_date, str):
        entry_date = datetime.fromisoformat(entry_date).date()

    status = entry_data.get("status", "done")
    notes = entry_data.get("notes")
    timestamp = entry_data.get("timestamp", datetime.utcnow())
    if isinstance(timestamp, str):
        timestamp = datetime.fromisoformat(timestamp)

    # Upsert: find existing
    existing = None
    try:
        existing = (
            db.query(DailyHabitEntry)
            .filter(
                DailyHabitEntry.user_id == user_id,
                DailyHabitEntry.habit_name == habit_name,
                DailyHabitEntry.date == entry_date,
            )
            .first()
        )
    except Exception:
        # If db isn't a SQLAlchemy session, try attribute access for dict/list style
        existing = None

    if existing:
        # Update allowed fields
        existing.status = status
        existing.notes = notes
        existing.timestamp = timestamp
        try:
            existing.updated_at = datetime.utcnow()
        except Exception:
            pass
        try:
            db.add(existing)
            db.commit()
            db.refresh(existing)
        except Exception:
            # If commit fails or session methods differ, assume persistent update
            pass
        return _entry_to_dict(existing)

    # Create new
    # Create new SQLAlchemy model instance. DailyHabitEntry defines a `timestamp` column
    # (and does not define created_at/updated_at columns), so pass only supported kwargs.
    new_entry = DailyHabitEntry(
        user_id=user_id,
        habit_name=habit_name,
        date=entry_date,
        status=status,
        notes=notes,
        timestamp=timestamp,
    )
    try:
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)
    except Exception:
        # If session isn't standard, try append to container or raise
        try:
            db.append(new_entry)
        except Exception:
            raise
    return _entry_to_dict(new_entry)


def get_habit_entry(db, entry_id: int) -> Dict[str, Any]:
    """Returns one entry by ID or raises ValueError if not found."""
    entry = None
    try:
        entry = db.query(DailyHabitEntry).filter(DailyHabitEntry.id == entry_id).first()
    except Exception:
        # fallback: try db.get
        try:
            entry = db.get(DailyHabitEntry, entry_id)
        except Exception:
            entry = None

    if not entry:
        raise ValueError(f"Habit entry not found: id={entry_id}")
    return _entry_to_dict(entry)


def update_habit_entry(db, entry_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Updates notes/status/timestamp fields of an entry.
    Raises ValueError if not found.
    """
    entry = None
    try:
        entry = db.query(DailyHabitEntry).filter(DailyHabitEntry.id == entry_id).first()
    except Exception:
        try:
            entry = db.get(DailyHabitEntry, entry_id)
        except Exception:
            entry = None

    if not entry:
        raise ValueError(f"Habit entry not found: id={entry_id}")

    allowed = {"notes", "status", "timestamp"}
    for k in allowed.intersection(update_data.keys()):
        v = update_data[k]
        if k == "timestamp" and isinstance(v, str):
            v = datetime.fromisoformat(v)
        setattr(entry, k, v)
    try:
        entry.updated_at = datetime.utcnow()
    except Exception:
        pass

    try:
        db.add(entry)
        db.commit()
        db.refresh(entry)
    except Exception:
        pass

    return _entry_to_dict(entry)


def delete_habit_entry(db, entry_id: int) -> None:
    """Deletes a record. Raises ValueError if not found."""
    entry = None
    try:
        entry = db.query(DailyHabitEntry).filter(DailyHabitEntry.id == entry_id).first()
    except Exception:
        try:
            entry = db.get(DailyHabitEntry, entry_id)
        except Exception:
            entry = None

    if not entry:
        raise ValueError(f"Habit entry not found: id={entry_id}")

    try:
        db.delete(entry)
        db.commit()
    except Exception:
        # If non-standard, try removing from container
        try:
            db.remove(entry)
        except Exception:
            raise


def get_user_habits(
    db, user_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None
) -> List[Dict[str, Any]]:
    """
    Returns all habits for a user in a date range (inclusive).
    If start_date/end_date are None returns all entries for user.
    """
    q = None
    try:
        q = db.query(DailyHabitEntry).filter(DailyHabitEntry.user_id == user_id)
        if start_date:
            if isinstance(start_date, str):
                start_date = datetime.fromisoformat(start_date).date()
            q = q.filter(DailyHabitEntry.date >= start_date)
        if end_date:
            if isinstance(end_date, str):
                end_date = datetime.fromisoformat(end_date).date()
            q = q.filter(DailyHabitEntry.date <= end_date)
        q = q.order_by(DailyHabitEntry.date.asc())
        entries = q.all()
    except Exception:
        # Fallback: iterate container if db is list-like
        entries = []
        try:
            for e in getattr(db, "entries", []) or db:
                if getattr(e, "user_id", None) != user_id:
                    continue
                e_date = getattr(e, "date", None)
                if start_date and e_date < start_date:
                    continue
                if end_date and e_date > end_date:
                    continue
                entries.append(e)
            entries.sort(key=lambda e: getattr(e, "date", None))
        except Exception:
            entries = []

    return [_entry_to_dict(e) for e in entries]


def compute_streaks(db, user_id: int, habit_name: str) -> Dict[str, Any]:
    """
    Calculates current_streak and max_streak for a given user and habit_name.
    Uses only entries with status equal to 'done' (case-insensitive).
    Returns a summary dict:
      {
        "user_id": ...,
        "habit_name": ...,
        "current_streak": int,
        "max_streak": int,
        "last_done_date": date or None,
        "done_dates": [date, ...]
      }
    """
    try:
        rows = (
            db.query(DailyHabitEntry)
            .filter(
                DailyHabitEntry.user_id == user_id,
                DailyHabitEntry.habit_name == habit_name,
            )
            .all()
        )
    except Exception:
        # fallback iterate
        rows = []
        try:
            for e in getattr(db, "entries", []) or db:
                if getattr(e, "user_id", None) == user_id and getattr(e, "habit_name", None) == habit_name:
                    rows.append(e)
        except Exception:
            rows = []

    done_dates = sorted(
        {getattr(r, "date") for r in rows if getattr(r, "status", "").lower() == "done"},
    )

    current_streak, max_streak = _calculate_streak(done_dates)
    last_done_date = done_dates[-1] if done_dates else None

    return {
        "user_id": user_id,
        "habit_name": habit_name,
        "current_streak": current_streak,
        "max_streak": max_streak,
        "last_done_date": last_done_date,
        "done_dates": done_dates,
    }


def compute_completion_rate(
    db, user_id: int, start_date: date, end_date: date
) -> Dict[str, Any]:
    """
    Returns completion summary for the time window (inclusive).
    Schema:
      {
        "user_id": ...,
        "start_date": ...,
        "end_date": ...,
        "total_entries": int,
        "total_done": int,
        "completion_rate": float   # done / total (0..1), 0 if total==0
      }
    """
    if isinstance(start_date, str):
        start_date = datetime.fromisoformat(start_date).date()
    if isinstance(end_date, str):
        end_date = datetime.fromisoformat(end_date).date()
    try:
        q = (
            db.query(DailyHabitEntry)
            .filter(DailyHabitEntry.user_id == user_id)
            .filter(DailyHabitEntry.date >= start_date)
            .filter(DailyHabitEntry.date <= end_date)
        )
        all_entries = q.all()
    except Exception:
        # fallback iteration
        all_entries = []
        try:
            for e in getattr(db, "entries", []) or db:
                if getattr(e, "user_id", None) != user_id:
                    continue
                ed = getattr(e, "date", None)
                if ed is None:
                    continue
                if ed < start_date or ed > end_date:
                    continue
                all_entries.append(e)
        except Exception:
            all_entries = []

    total_entries = len(all_entries)
    total_done = sum(1 for e in all_entries if getattr(e, "status", "").lower() == "done")
    completion_rate = (total_done / total_entries) if total_entries > 0 else 0.0

    return {
        "user_id": user_id,
        "start_date": start_date,
        "end_date": end_date,
        "total_entries": total_entries,
        "total_done": total_done,
        "completion_rate": completion_rate,
    }