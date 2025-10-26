"""
API Client for MindTrack Frontend
Connects Streamlit frontend to FastAPI backend
"""
import requests
from typing import Dict, List, Any, Optional
from datetime import date

class MindTrackAPI:
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize API client with base URL"""
        self.base_url = base_url
        self.session = requests.Session()
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to backend"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, **kwargs)
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as he:
                # Include response body in exception for better debugging
                resp_text = None
                try:
                    resp_text = response.text
                except Exception:
                    resp_text = str(he)
                raise Exception(f"API request failed: {response.status_code} {response.reason} - {resp_text}")

            # Return parsed JSON if possible, otherwise return raw text
            try:
                return response.json()
            except ValueError:
                return {"text": response.text}
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
    
    # User endpoints
    def create_user(self, name: str, timezone: Optional[str] = None, preferences: Dict = None) -> Dict:
        """Create a new user"""
        data = {
            "name": name,
            "timezone": timezone or "UTC",
            "preferences": preferences or {}
        }
        return self._request("POST", "/users/", json=data)
    
    def get_user(self, user_id: str) -> Dict:
        """Get user by ID"""
        return self._request("GET", f"/users/{user_id}")
    
    def update_preferences(self, user_id: str, preferences: Dict) -> Dict:
        """Update user preferences"""
        return self._request("PUT", f"/users/{user_id}/preferences", json=preferences)
    
    # Habit endpoints
    def create_habit_entry(self, user_id: str, habit_name: str, entry_date: str,
                          status: str = "done", target_value: Optional[float] = None,
                          notes: Optional[str] = None, mood: Optional[float] = None) -> Dict:
        """Create a habit entry. Uses 'entry_date' key to match backend schema."""
        data = {
            "user_id": user_id,
            "habit_name": habit_name,
            "entry_date": entry_date,
            "status": status,
            "target_value": target_value,
            "notes": notes,
            "mood": mood
        }
        return self._request("POST", "/habits/", json=data)
    
    def get_user_habits(self, user_id: str, start_date: Optional[str] = None, 
                       end_date: Optional[str] = None) -> List[Dict]:
        """Get user's habit entries"""
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        
        response = self._request("GET", f"/habits/user/{user_id}", params=params)
        return response if isinstance(response, list) else []
    
    def get_streaks(self, user_id: str, habit_name: str) -> Dict:
        """Get streak information for a habit"""
        return self._request("GET", f"/habits/user/{user_id}/streaks", 
                           params={"habit_name": habit_name})
    
    def get_completion_rate(self, user_id: str, start_date: str, end_date: str) -> Dict:
        """Get completion rate for date range"""
        return self._request("GET", f"/habits/user/{user_id}/completion",
                           params={"start_date": start_date, "end_date": end_date})
    
    # Badge endpoints
    def get_badges(self, user_id: str) -> List[Dict]:
        """Get user's badges"""
        response = self._request("GET", f"/badges/user/{user_id}")
        return response if isinstance(response, list) else []
    
    def check_and_award_badges(self, user_id: str) -> Dict:
        """Check and award badges based on streaks"""
        return self._request("POST", f"/badges/award-check/{user_id}")
    
    # Insights endpoints
    def get_insights(self, user_id: str, days: int = 30) -> Dict:
        """Get comprehensive insights for user"""
        return self._request("GET", f"/insights/user/{user_id}", 
                           params={"days": days})
    
    # ML Prediction endpoints
    def predict_sleep(self, total_steps: int, very_active_minutes: int, 
                     fairly_active_minutes: int, lightly_active_minutes: int,
                     sedentary_minutes: int, calories: int,
                     avg_steps_7d: Optional[float] = None,
                     prev_day_sleep: Optional[float] = None,
                     is_weekend: int = 0) -> Dict:
        """Predict sleep duration based on activity"""
        data = {
            "total_steps": total_steps,
            "very_active_minutes": very_active_minutes,
            "fairly_active_minutes": fairly_active_minutes,
            "lightly_active_minutes": lightly_active_minutes,
            "sedentary_minutes": sedentary_minutes,
            "calories": calories,
            "avg_steps_7d": avg_steps_7d or total_steps,
            "prev_day_sleep": prev_day_sleep or 480.0,
            "is_weekend": is_weekend
        }
        return self._request("POST", "/predictions/sleep", json=data)

# Global API instance
api = MindTrackAPI()

