from typing import Any, Dict, List, Optional
from datetime import datetime
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

# /c:/Users/Sweta.Singh/Downloads/project/tts/new/backend/app/services/reminder_service.py


from app.models import Reminder  # adjust import path if your project structure differs

logger = logging.getLogger(__name__)


class ReminderNotFoundError(LookupError):
    pass


class ReminderValidationError(ValueError):
    pass


def _validate_time_of_day(time_str: str) -> None:
    """
    Validate that time_str is in HH:MM 24-hour format.
    Raises ReminderValidationError on failure.
    """
    try:
        datetime.strptime(time_str, "%H:%M")
    except (ValueError, TypeError):
        raise ReminderValidationError(f"time_of_day must be 'HH:MM' 24-hour format, got: {time_str!r}")


def _ensure_reminder_schema(data: Dict[str, Any]) -> None:
    """
    Ensure incoming data has only allowed keys for the Reminder object.
    This is intentionally permissive for optional fields but prevents arbitrary keys.
    """
    allowed_keys = {"user_id", "message", "time_of_day", "repeat", "enabled"}
    extra = set(data.keys()) - allowed_keys
    if extra:
        raise ReminderValidationError(f"Unexpected fields in reminder data: {sorted(extra)}")


def create_reminder(db: Session, reminder_data: Dict[str, Any]) -> Reminder:
    """
    Insert a new reminder into the DB after validating the payload.

    Required keys: user_id, message, time_of_day
    Optional: repeat, enabled

    Returns the created Reminder object.
    """
    logger.debug("create_reminder called with data: %s", reminder_data)
    _ensure_reminder_schema(reminder_data)

    # required fields validation
    for required in ("user_id", "message", "time_of_day"):
        if required not in reminder_data:
            logger.error("Missing required field %s in reminder_data", required)
            raise ReminderValidationError(f"Missing required field: {required}")

    _validate_time_of_day(reminder_data["time_of_day"])

    # set defaults
    reminder_payload = {
        "user_id": reminder_data["user_id"],
        "message": reminder_data["message"],
        "time_of_day": reminder_data["time_of_day"],
        "repeat": reminder_data.get("repeat"),
        "enabled": bool(reminder_data.get("enabled", True)),
    }

    try:
        reminder = Reminder(**reminder_payload)
        db.add(reminder)
        db.commit()
        db.refresh(reminder)
        logger.info("Created reminder id=%s for user=%s", getattr(reminder, "id", None), reminder.user_id)
        return reminder
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception("Database error creating reminder: %s", e)
        raise


def get_reminder(db: Session, reminder_id: int) -> Reminder:
    """
    Return a Reminder by ID or raise ReminderNotFoundError.
    """
    logger.debug("get_reminder called for id=%s", reminder_id)
    reminder = db.query(Reminder).get(reminder_id)  # type: ignore[attr-defined]
    if reminder is None:
        logger.warning("Reminder not found id=%s", reminder_id)
        raise ReminderNotFoundError(f"Reminder not found: {reminder_id}")
    return reminder


def list_reminders_for_user(db: Session, user_id: int) -> List[Reminder]:
    """
    Return all reminders for a given user_id.
    """
    logger.debug("list_reminders_for_user called for user_id=%s", user_id)
    reminders = db.query(Reminder).filter(Reminder.user_id == user_id).all()
    logger.info("Found %d reminders for user_id=%s", len(reminders), user_id)
    return reminders


def update_reminder(db: Session, reminder_id: int, update_data: Dict[str, Any]) -> Reminder:
    """
    Update allowed fields for a reminder: time_of_day, repeat, enabled.
    Validate time_of_day format if present.
    Returns the updated Reminder.
    """
    logger.debug("update_reminder id=%s data=%s", reminder_id, update_data)
    allowed_update_fields = {"time_of_day", "repeat", "enabled"}
    extra = set(update_data.keys()) - allowed_update_fields
    if extra:
        logger.error("Attempt to update disallowed fields: %s", extra)
        raise ReminderValidationError(f"Cannot update fields: {sorted(extra)}")

    if "time_of_day" in update_data:
        _validate_time_of_day(update_data["time_of_day"])

    reminder = get_reminder(db, reminder_id)

    # apply updates
    if "time_of_day" in update_data:
        reminder.time_of_day = update_data["time_of_day"]
    if "repeat" in update_data:
        reminder.repeat = update_data["repeat"]
    if "enabled" in update_data:
        reminder.enabled = bool(update_data["enabled"])

    try:
        db.add(reminder)
        db.commit()
        db.refresh(reminder)
        logger.info("Updated reminder id=%s", reminder_id)
        return reminder
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception("Database error updating reminder id=%s: %s", reminder_id, e)
        raise


def delete_reminder(db: Session, reminder_id: int) -> None:
    """
    Delete a reminder record. Raises ReminderNotFoundError if missing.
    """
    logger.debug("delete_reminder called for id=%s", reminder_id)
    reminder = get_reminder(db, reminder_id)
    try:
        db.delete(reminder)
        db.commit()
        logger.info("Deleted reminder id=%s", reminder_id)
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception("Database error deleting reminder id=%s: %s", reminder_id, e)
        raise


def get_due_reminders(db: Session, current_time: datetime) -> List[Reminder]:
    """
    Return reminders that should trigger at the provided current_time.

    The logic:
    - Matches reminders with enabled == True and time_of_day == HH:MM of current_time.
    - Returns all such reminders. If your model stores next_run or one-off flags,
      additional logic should be added to handle one-time reminders (e.g., disable them after firing).

    Returns a list of Reminder objects.
    """
    time_str = current_time.strftime("%H:%M")
    logger.debug("get_due_reminders called for time=%s", time_str)
    reminders = db.query(Reminder).filter(Reminder.enabled == True, Reminder.time_of_day == time_str).all()
    logger.info("Found %d due reminders for time=%s", len(reminders), time_str)
    return reminders