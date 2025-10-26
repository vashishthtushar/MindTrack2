from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from datetime import date, timedelta

from app.db.database import get_db
from app.services import habit_service, badge_service

router = APIRouter()

@router.get("/user/{user_id}")
async def get_user_insights(user_id: str, days: int = 30, db: Session = Depends(get_db)):
    """Get comprehensive insights for a user"""
    try:
        # Calculate date range
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Get completion rate
        completion = habit_service.compute_completion_rate(db, user_id, start_date, end_date)
        
        # Get habit entries for streak calculation
        entries = habit_service.get_user_habits(db, user_id, start_date, end_date)
        
        # Calculate insights for each habit
        habit_insights = {}
        unique_habits = set(entry.get("habit_name") for entry in entries)
        
        for habit_name in unique_habits:
            try:
                streaks = habit_service.compute_streaks(db, user_id, habit_name)
                habit_insights[habit_name] = {
                    "current_streak": streaks.get("current_streak", 0),
                    "max_streak": streaks.get("max_streak", 0),
                    "last_done_date": streaks.get("last_done_date")
                }
            except Exception:
                habit_insights[habit_name] = {
                    "current_streak": 0,
                    "max_streak": 0,
                    "last_done_date": None
                }
        
        # Get recent badges
        try:
            badges = badge_service.get_user_badges(db, user_id)
            recent_badges = sorted(badges, key=lambda x: x.get("awarded_at", ""), reverse=True)[:5]
        except Exception:
            recent_badges = []
        
        # Generate recommendations
        recommendations = []
        
        if completion.get("completion_rate", 0) < 0.7:
            recommendations.append({
                "title": "Improve Consistency",
                "body": f"Your completion rate is {completion['completion_rate']*100:.1f}%. Try to complete at least {completion['total_entries'] - completion['total_done']} more entries.",
                "confidence": "high" if completion.get("total_entries", 0) > 10 else "medium"
            })
        
        # Find strongest habit
        if habit_insights:
            best_habit = max(habit_insights.items(), key=lambda x: x[1].get("current_streak", 0))
            if best_habit[1]["current_streak"] >= 3:
                recommendations.append({
                    "title": "Maintain Your Momentum",
                    "body": f"Great work on your {best_habit[0]} streak! You've maintained it for {best_habit[1]['current_streak']} days.",
                    "confidence": "high"
                })
        
        return {
            "user_id": user_id,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            },
            "completion_rate": completion.get("completion_rate", 0),
            "total_entries": completion.get("total_entries", 0),
            "total_done": completion.get("total_done", 0),
            "habit_streaks": habit_insights,
            "recent_badges": recent_badges,
            "recommendations": recommendations
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate insights: {str(e)}"
        )

