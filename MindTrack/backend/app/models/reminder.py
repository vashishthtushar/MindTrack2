import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional
from pydantic import BaseModel, Field
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum as SQLEnum
from app.db.database import Base


class RepeatEnum(PyEnum):
    DAILY = "daily"
    WEEKLY = "weekly"
    CUSTOM = "custom"


class Reminder(Base):
    """
    Reminder model for scheduled habit reminders.

    Fields:
    - reminder_id: UUID primary key
    - user_id: FK -> users.user_id
    - habit_name: name of the habit
    - time_of_day: string HH:MM
    - repeat: enum (daily, weekly, custom)
    - enabled: boolean, default True
    - created_at: timestamp when created
    - last_triggered: timestamp when last triggered (nullable)

    Relationship:
    - many-to-one with User (user.reminders)
    """
    __tablename__ = "reminders"

    reminder_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    habit_name = Column(String(255), nullable=False)
    time_of_day = Column(String(5), nullable=False)  # format HH:MM
    repeat = Column(SQLEnum(RepeatEnum, name="reminder_repeat", native_enum=False), nullable=False, default=RepeatEnum.DAILY.value)
    enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_triggered = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="reminders")


# Pydantic schemas
class ReminderBase(BaseModel):
    habit_name: str = Field(..., max_length=255)
    time_of_day: str = Field(..., pattern=r"^\d{2}:\d{2}$")  # HH:MM
    repeat: RepeatEnum = RepeatEnum.DAILY
    enabled: bool = True


class ReminderCreate(ReminderBase):
    user_id: uuid.UUID


class ReminderResponse(ReminderBase):
    reminder_id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    last_triggered: Optional[datetime] = None

    class Config:
        from_attributes = True