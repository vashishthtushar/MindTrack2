import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List
from sqlalchemy import text
from app.services import habit_service

# badge_service.py
"""
Badge service for user gamification.

Responsibilities implemented:
- check_and_award_streak_badges(db, user_id)
- get_user_badges(db, user_id)
- award_custom_badge(db, user_id, name, description)
- badge_exists(db, user_id, name)

Assumptions:
- There is a database table named "badges" with at least the columns:
    id (UUID/text), user_id, name, description, awarded_at (timestamp)
- `db` is a SQLAlchemy Session, Connection, or Engine-like object that supports
  .execute(...) and .begin() context manager.
- habit_service.compute_streaks(db, user_id) exists and returns either:
    - an integer (current streak length),
    - a dict containing 'current_streak' key,
    - or an iterable of streak values (we will take the max).
"""



# Import habit_service (must be available in your project)

logger = logging.getLogger(__name__)

# Milestone days for streak badges
STREAK_MILESTONES = (3, 7, 14, 30)


def _now_iso() -> str:
    # Use ISO 8601 UTC timestamp string for awarded_at
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def _row_to_dict(row: Any) -> Dict[str, Any]:
    # Convert SQLAlchemy Row / mapping to a plain dict
    try:
        return dict(row._mapping)
    except Exception:
        try:
            return dict(row)
        except Exception:
            return {}


def badge_exists(db: Any, user_id: str, name: str) -> bool:
    """
    Return True if a badge with this name already exists for the user.
    """
    sql = text(
        "SELECT 1 FROM badges WHERE user_id = :user_id AND name = :name LIMIT 1"
    )
    result = db.execute(sql, {"user_id": user_id, "name": name})
    row = result.first()
    exists = row is not None
    logger.debug("badge_exists user=%s name=%s => %s", user_id, name, exists)
    return exists


def get_user_badges(db: Any, user_id: str) -> List[Dict[str, Any]]:
    """
    Return all badges for a user as a list of dicts.
    """
    sql = text("SELECT * FROM badges WHERE user_id = :user_id ORDER BY awarded_at DESC")
    result = db.execute(sql, {"user_id": user_id})
    rows = result.fetchall()
    return [_row_to_dict(r) for r in rows]


def award_custom_badge(db: Any, user_id: str, name: str, description: str) -> Dict[str, Any]:
    """
    Insert a new badge record for the user. Prevents duplicates by name.
    Returns the created badge dict on success.
    Raises ValueError if the badge already exists.
    """
    if badge_exists(db, user_id, name):
        raise ValueError(f"Badge '{name}' already exists for user {user_id}")

    badge_id = str(uuid.uuid4())
    awarded_at = _now_iso()

    insert_sql = text(
        "INSERT INTO badges (id, user_id, name, description, awarded_at) "
        "VALUES (:id, :user_id, :name, :description, :awarded_at)"
    )
    params = {
        "id": badge_id,
        "user_id": user_id,
        "name": name,
        "description": description,
        "awarded_at": awarded_at,
    }

    # Atomic insert with transaction
    with db.begin():
        db.execute(insert_sql, params)

    badge = {
        "id": badge_id,
        "user_id": user_id,
        "name": name,
        "description": description,
        "awarded_at": awarded_at,
    }
    logger.info("Awarded custom badge to user=%s name=%s", user_id, name)
    return badge


def _normalize_streak_value(streaks: Any) -> int:
    """
    Accept different return shapes from habit_service.compute_streaks:
    - int => return as-is
    - dict with 'current_streak' => return that
    - iterable => return max value
    """
    if streaks is None:
        return 0
    if isinstance(streaks, int):
        return streaks
    if isinstance(streaks, dict):
        # prefer 'current_streak' if present
        if "current_streak" in streaks:
            try:
                return int(streaks["current_streak"])
            except Exception:
                pass
        # fallback: try values
        try:
            return int(max(streaks.values()))
        except Exception:
            return 0
    # iterable case
    try:
        iterable = list(streaks)
        if not iterable:
            return 0
        return int(max(iterable))
    except Exception:
        return 0


def check_and_award_streak_badges(db: Any, user_id: str) -> List[Dict[str, Any]]:
    """
    Check user's streaks using habit_service.compute_streaks and award badges
    for milestones (3, 7, 14, 30 days). Avoid duplicates. Returns a list of
    awarded badge dicts (may be empty).
    """
    # Fetch streak information from habit_service
    try:
        raw_streaks = habit_service.compute_streaks(db, user_id)
    except Exception as e:
        logger.exception("Failed to compute streaks for user=%s: %s", user_id, e)
        return []

    current_streak = _normalize_streak_value(raw_streaks)
    logger.debug("User %s current_streak=%s (raw=%s)", user_id, current_streak, raw_streaks)

    awards: List[Dict[str, Any]] = []

    # Determine which milestones are reached and not already awarded
    for milestone in STREAK_MILESTONES:
        if current_streak >= milestone:
            name = f"{milestone}-Day Streak"
            description = f"Awarded for maintaining a {milestone}-day streak."
            try:
                if not badge_exists(db, user_id, name):
                    badge_id = str(uuid.uuid4())
                    awarded_at = _now_iso()
                    insert_sql = text(
                        "INSERT INTO badges (id, user_id, name, description, awarded_at) "
                        "VALUES (:id, :user_id, :name, :description, :awarded_at)"
                    )
                    params = {
                        "id": badge_id,
                        "user_id": user_id,
                        "name": name,
                        "description": description,
                        "awarded_at": awarded_at,
                    }
                    # Use atomic transaction per award batch to ensure all-or-nothing:
                    # we will group all inserts into a single transaction below.
                    awards.append({"id": badge_id, "user_id": user_id, "name": name, "description": description, "awarded_at": awarded_at})
                else:
                    logger.debug("Badge already exists: user=%s name=%s", user_id, name)
            except Exception:
                logger.exception("Error checking/creating badge existence for user=%s name=%s", user_id, name)

    if not awards:
        return []

    # Perform insertion of all new awards within a single atomic transaction
    try:
        with db.begin():
            for badge in awards:
                insert_sql = text(
                    "INSERT INTO badges (id, user_id, name, description, awarded_at) "
                    "VALUES (:id, :user_id, :name, :description, :awarded_at)"
                )
                db.execute(insert_sql, badge)
        for b in awards:
            logger.info("Awarded badge user=%s name=%s", user_id, b["name"])
    except Exception as e:
        logger.exception("Failed to commit awarded badges for user=%s: %s", user_id, e)
        return []

    return awards