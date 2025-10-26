from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import date

from app.db.database import get_db
from app.models.habit_entry import HabitEntryCreate, HabitEntryResponse
from app.services import habit_service

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_habit_entry(entry: HabitEntryCreate, db: Session = Depends(get_db)):
    """Create a new habit entry"""
    try:
        entry_data = {
            "user_id": str(entry.user_id),
            "habit_name": entry.habit_name,
            "date": entry.entry_date,  # Use the correct field name
            "target_value": entry.target_value,
            "status": entry.status,
            "notes": entry.notes,
            "mood": entry.mood
        }
        created_entry = habit_service.create_habit_entry(db, entry_data)
        return created_entry
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create habit entry: {str(e)}"
        )

@router.get("/user/{user_id}", response_model=List[Dict[str, Any]])
async def get_user_habits(
    user_id: str,
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db)
):
    """Get all habit entries for a user, optionally filtered by date range"""
    try:
        entries = habit_service.get_user_habits(db, user_id, start_date, end_date)
        return entries
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get habit entries: {str(e)}"
        )

@router.get("/user/{user_id}/streaks", response_model=Dict[str, Any])
async def get_user_streaks(user_id: str, habit_name: str, db: Session = Depends(get_db)):
    """Get streak information for a specific habit"""
    try:
        streaks = habit_service.compute_streaks(db, user_id, habit_name)
        return streaks
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to compute streaks: {str(e)}"
        )

@router.get("/user/{user_id}/completion", response_model=Dict[str, Any])
async def get_completion_rate(
    user_id: str,
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db)
):
    """Get completion rate for a date range"""
    try:
        completion = habit_service.compute_completion_rate(db, user_id, start_date, end_date)
        return completion
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to compute completion rate: {str(e)}"
        )

@router.put("/{entry_id}")
async def update_habit_entry(entry_id: str, update_data: dict, db: Session = Depends(get_db)):
    """Update a habit entry"""
    try:
        updated_entry = habit_service.update_habit_entry(db, entry_id, update_data)
        return updated_entry
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update habit entry: {str(e)}"
        )

@router.delete("/{entry_id}")
async def delete_habit_entry(entry_id: str, db: Session = Depends(get_db)):
    """Delete a habit entry"""
    try:
        habit_service.delete_habit_entry(db, entry_id)
        return {"message": "Habit entry deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete habit entry: {str(e)}"
        )

