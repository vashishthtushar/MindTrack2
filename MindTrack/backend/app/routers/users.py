from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.db.database import get_db
from app.models.user import User, UserCreate, UserResponse
from app.services.user_service import create_user, get_user, list_users, update_preferences

router = APIRouter()

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    try:
        new_user = create_user(db, user)
        return UserResponse(
            user_id=str(new_user.user_id),  # Convert UUID to string
            name=new_user.name,
            timezone=new_user.timezone,
            created_at=new_user.created_at,
            preferences=new_user.preferences
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create user: {str(e)}"
        )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_endpoint(user_id: str, db: Session = Depends(get_db)):
    """Get user by ID"""
    try:
        user = get_user(db, user_id)
        return UserResponse(
            user_id=str(user.user_id),  # Convert UUID to string
            name=user.name,
            timezone=user.timezone,
            created_at=user.created_at,
            preferences=user.preferences
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/", response_model=List[UserResponse])
async def list_all_users(db: Session = Depends(get_db)):
    """List all users"""
    try:
        users = list_users(db)
        return [
            UserResponse(
                user_id=str(u.user_id),  # Convert UUID to string
                name=u.name,
                timezone=u.timezone,
                created_at=u.created_at,
                preferences=u.preferences
            )
            for u in users
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list users: {str(e)}"
        )

@router.put("/{user_id}/preferences")
async def update_user_preferences(user_id: str, preferences: dict, db: Session = Depends(get_db)):
    """Update user preferences"""
    try:
        updated_user = update_preferences(db, user_id, preferences)
        return {
            "message": "Preferences updated successfully",
            "user_id": str(updated_user.user_id),
            "preferences": updated_user.preferences
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

