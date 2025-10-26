import datetime
from typing import Optional, TYPE_CHECKING
from uuid import UUID, uuid4
from pydantic import BaseModel
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship, Session
from app.db.database import Base

if TYPE_CHECKING:
    from app.models.user import User  # for type hints only


class Badge(Base):
    __tablename__ = "badges"

    badge_id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False, unique=True)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String, nullable=True)
    awarded_at = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow)

    # relationship: many badges -> one user
    user = relationship("User", back_populates="badges")


def award_badge(session: Session, user_id: UUID, name: str, description: Optional[str] = None) -> Badge:
    """
    Create and persist a Badge for the given user_id.
    Commits the session and returns the refreshed Badge instance.
    """
    badge = Badge(user_id=user_id, name=name, description=description)
    session.add(badge)
    session.commit()
    session.refresh(badge)
    return badge


# Pydantic schemas

class BadgeBase(BaseModel):
    name: str
    description: Optional[str] = None


class BadgeCreate(BadgeBase):
    user_id: UUID


class BadgeResponse(BadgeBase):
    badge_id: UUID
    user_id: UUID
    awarded_at: datetime.datetime

    class Config:
        from_attributes = True