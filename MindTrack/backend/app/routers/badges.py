from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.db.database import get_db
from app.services import badge_service

router = APIRouter()

@router.get("/user/{user_id}", response_model=List[Dict[str, Any]])
async def get_user_badges(user_id: str, db: Session = Depends(get_db)):
    """Get all badges for a user"""
    try:
        badges = badge_service.get_user_badges(db, user_id)
        return badges
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get badges: {str(e)}"
        )

@router.post("/award-check/{user_id}")
async def check_and_award_badges(user_id: str, db: Session = Depends(get_db)):
    """Check user streaks and award badges if milestones are reached"""
    try:
        awarded_badges = badge_service.check_and_award_streak_badges(db, user_id)
        return {
            "message": f"Checked badges for user {user_id}",
            "awarded_count": len(awarded_badges),
            "badges": awarded_badges
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to check/award badges: {str(e)}"
        )

@router.post("/custom/{user_id}")
async def award_custom_badge(user_id: str, name: str, description: str, db: Session = Depends(get_db)):
    """Award a custom badge to a user"""
    try:
        badge = badge_service.award_custom_badge(db, user_id, name, description)
        return badge
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to award badge: {str(e)}"
        )

