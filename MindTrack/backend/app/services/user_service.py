import uuid
from datetime import datetime
from typing import Any, Dict, List, Union
from sqlalchemy import String as SAString
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.models.user import User, UserCreate

class NotFoundError(Exception):
    """Simple 404-style exception carrying a message and status_code=404."""

    status_code = 404

    def __init__(self, detail: str):
        super().__init__(detail)
        self.detail = detail


def _normalize_uuid_for_column(user_id: Union[str, uuid.UUID]) -> Union[str, uuid.UUID]:
    """
    Normalize a uuid.UUID to string when the User.user_id column is a string type.
    This helps comparisons to work regardless of whether the DB column stores UUID natively.
    """
    col_type = User.__table__.c.user_id.type
    if isinstance(col_type, SAString) and isinstance(user_id, uuid.UUID):
        return str(user_id)
    return user_id


def create_user(db: Session, user_data: UserCreate) -> User:
    """
    Create a new user record.

    - Generates a UUID for user_id (string if DB uses string storage).
    - Sets created_at to datetime.utcnow().
    - Commits the new user to the DB and refreshes the instance.

    Returns the created User ORM instance.

    Raises SQLAlchemyError on DB errors.
    """
    try:
        # pick an appropriate representation for the UUID column
        raw_uuid = uuid.uuid4()
        col_type = User.__table__.c.user_id.type
        user_id_value = str(raw_uuid) if isinstance(col_type, SAString) else raw_uuid

        new_user = User(
            user_id=user_id_value,
            name=user_data.name,
            timezone=user_data.timezone,
            preferences=user_data.preferences or {},
            created_at=datetime.utcnow(),
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except SQLAlchemyError:
        db.rollback()
        raise


def get_user(db: Session, user_id: Union[str, uuid.UUID]) -> User:
    """
    Retrieve a single user by user_id.

    Raises NotFoundError (404-style) if user is not found.
    """
    try:
        normalized = _normalize_uuid_for_column(user_id)
        user = db.query(User).filter(User.user_id == normalized).one_or_none()
        if user is None:
            raise NotFoundError(f"User with id={user_id} not found")
        return user
    except SQLAlchemyError:
        # bubble up DB errors as-is
        raise


def list_users(db: Session) -> List[User]:
    """
    Return all users in the system.
    """
    try:
        return db.query(User).all()
    except SQLAlchemyError:
        raise


def update_preferences(db: Session, user_id: Union[str, uuid.UUID], preferences: Dict[str, Any]) -> User:
    """
    Update the preferences JSON for the given user.

    Commits and refreshes the user instance before returning.

    Raises NotFoundError if the user does not exist.
    """
    try:
        user = get_user(db, user_id)
        user.preferences = preferences or {}
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except NotFoundError:
        # propagate 404-style exception
        raise
    except SQLAlchemyError:
        db.rollback()
        raise