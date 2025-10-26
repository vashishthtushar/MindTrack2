import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSON as PGJSON
from sqlalchemy import JSON as SA_JSON

# /c:/Users/Sweta.Singh/Downloads/project/tts/new/backend/app/models/user.py
# This module defines the User model for the application, including its attributes,
# Try to use PostgreSQL-specific types when available; fall back to generic SQLAlchemy types.
try:

    UUID_TYPE = PGUUID(as_uuid=True)
    JSON_TYPE = PGJSON
except Exception:

    UUID_TYPE = String(36)
    JSON_TYPE = SA_JSON

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    # Primary key: UUID. Use DB-native UUID when available, otherwise store as string.
    if isinstance(UUID_TYPE, String):
        user_id = Column(UUID_TYPE, primary_key=True, default=lambda: str(uuid.uuid4()))
    else:
        user_id = Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)

    name = Column(String(length=255), nullable=False)
    timezone = Column(String(length=64), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Preferences stored as JSON; use Postgres JSON if available or generic JSON otherwise.
    preferences = Column(JSON_TYPE, nullable=False, default=dict)

    # Relationships (defined by string to avoid circular imports). These referenced models
    # should define back_populates='user' on their side.
    daily_habit_entries = relationship(
        "DailyHabitEntry", back_populates="user", cascade="all, delete-orphan", lazy="select"
    )
    reminders = relationship(
        "Reminder", back_populates="user", cascade="all, delete-orphan", lazy="select"
    )
    badges = relationship(
        "Badge", back_populates="user", cascade="all, delete-orphan", lazy="select"
    )
    sensor_summaries = relationship(
        "SensorSummary", back_populates="user", cascade="all, delete-orphan", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<User user_id={self.user_id!s} name={self.name!r}>"


# Pydantic schemas

class UserBase(BaseModel):
    name: str
    timezone: Optional[str] = None
    preferences: Dict[str, Any] = Field(default_factory=dict)


class UserCreate(UserBase):
    """Schema for creating a new user. Inherits name, timezone, preferences."""


class UserResponse(UserBase):
    user_id: str  # Changed to string for API compatibility
    created_at: datetime

    class Config:
        from_attributes = True