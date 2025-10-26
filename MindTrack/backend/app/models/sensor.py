from datetime import date
from typing import Optional
from pydantic import BaseModel, Field
from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.db.database import Base

class SensorSummary(Base):
    __tablename__ = "sensor_summaries"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)

    date = Column(Date, nullable=False)

    total_steps = Column(Integer, nullable=False, default=0)
    very_active_minutes = Column(Integer, nullable=False, default=0)
    fairly_active_minutes = Column(Integer, nullable=False, default=0)
    lightly_active_minutes = Column(Integer, nullable=False, default=0)
    sedentary_minutes = Column(Integer, nullable=False, default=0)

    calories = Column(Integer, nullable=False, default=0)
    minutes_asleep = Column(Integer, nullable=False, default=0)

    data_source = Column(String(128), nullable=True)

    # relationship: many-to-one with User
    user = relationship("User", back_populates="sensor_summaries")

    @property
    def total_active_minutes(self) -> int:
        return (
            (self.very_active_minutes or 0)
            + (self.fairly_active_minutes or 0)
            + (self.lightly_active_minutes or 0)
        )


# Pydantic schemas

class SensorSummaryBase(BaseModel):
    date: date
    total_steps: int = 0
    very_active_minutes: int = 0
    fairly_active_minutes: int = 0
    lightly_active_minutes: int = 0
    sedentary_minutes: int = 0
    calories: int = 0
    minutes_asleep: int = 0
    data_source: Optional[str] = None

    class Config:
        from_attributes = True


class SensorSummaryCreate(SensorSummaryBase):
    user_id: int = Field(..., description="Foreign key to User.user_id")


class SensorSummaryResponse(SensorSummaryBase):
    id: int
    user_id: int
    total_active_minutes: int

    class Config:
        from_attributes = True