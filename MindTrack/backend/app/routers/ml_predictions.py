from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import os
import joblib
import pandas as pd
import numpy as np

router = APIRouter()

# Load ML pipeline at startup
PIPELINE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "pipeline.pkl")
ml_pipeline = None

def load_pipeline():
    """Load the ML pipeline from disk"""
    global ml_pipeline
    if ml_pipeline is None:
        try:
            if os.path.exists(PIPELINE_PATH):
                ml_pipeline = joblib.load(PIPELINE_PATH)
                print(f"Loaded ML pipeline from {PIPELINE_PATH}")
            else:
                print(f"Warning: ML pipeline not found at {PIPELINE_PATH}")
                ml_pipeline = None
        except Exception as e:
            print(f"Warning: Could not load ML pipeline: {e}")
            ml_pipeline = None
    return ml_pipeline

# Pydantic model for sleep prediction request
class SleepPredictionRequest(BaseModel):
    total_steps: int = Field(..., description="Total steps for the day")
    very_active_minutes: int = Field(..., description="Very active minutes")
    fairly_active_minutes: int = Field(..., description="Fairly active minutes")
    lightly_active_minutes: int = Field(..., description="Lightly active minutes")
    sedentary_minutes: int = Field(..., description="Sedentary minutes")
    calories: int = Field(..., description="Calories burned")
    avg_steps_7d: Optional[float] = Field(None, description="7-day average steps")
    prev_day_sleep: Optional[float] = Field(None, description="Previous day's sleep in minutes")
    is_weekend: int = Field(0, description="Is weekend (1) or weekday (0)")

    class Config:
        json_schema_extra = {
            "example": {
                "total_steps": 10198,
                "very_active_minutes": 17,
                "fairly_active_minutes": 20,
                "lightly_active_minutes": 195,
                "sedentary_minutes": 1208,
                "calories": 1755,
                "avg_steps_7d": 12157.0,
                "prev_day_sleep": 480.0,
                "is_weekend": 0
            }
        }

@router.post("/sleep", response_model=Dict[str, Any])
async def predict_sleep(request: SleepPredictionRequest):
    """Predict sleep duration based on activity data"""
    try:
        # Load pipeline if not already loaded
        pipeline = load_pipeline()
        
        if pipeline is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="ML pipeline not available. Please ensure pipeline.pkl exists in the data directory."
            )
        
        # Convert request to DataFrame
        input_data = {
            "TotalSteps": request.total_steps,
            "VeryActiveMinutes": request.very_active_minutes,
            "FairlyActiveMinutes": request.fairly_active_minutes,
            "LightlyActiveMinutes": request.lightly_active_minutes,
            "SedentaryMinutes": request.sedentary_minutes,
            "Calories": request.calories,
            "total_active_minutes": (request.very_active_minutes + 
                                   request.fairly_active_minutes + 
                                   request.lightly_active_minutes),
            "avg_steps_7d": request.avg_steps_7d or request.total_steps,
            "prev_day_sleep": request.prev_day_sleep or 480.0,  # default to 8 hours
            "is_weekend": request.is_weekend
        }
        
        df = pd.DataFrame([input_data])
        
        # Make prediction
        prediction = pipeline.predict(df)[0]
        
        # Get feature importances if available
        feature_importance = {}
        try:
            model = pipeline.named_steps['model']
            if hasattr(model, 'feature_importances_'):
                # Get feature names from the preprocessor
                preprocessor = pipeline.named_steps['preprocessor']
                if hasattr(preprocessor, 'get_feature_names_out'):
                    feature_names = preprocessor.get_feature_names_out()
                else:
                    # Fallback for older sklearn versions
                    feature_names = [f"feature_{i}" for i in range(len(model.feature_importances_))]
                
                importances = model.feature_importances_
                feature_importance = dict(zip(feature_names, importances))
                # Sort by importance
                feature_importance = dict(sorted(feature_importance.items(), 
                                                key=lambda x: x[1], 
                                                reverse=True))
        except Exception as e:
            print(f"Could not get feature importances: {e}")
            pass  # Feature importances not available
        
        # Round prediction to nearest minute
        prediction_minutes = round(prediction)
        
        # Convert to hours and minutes for readability
        hours = prediction_minutes // 60
        minutes = prediction_minutes % 60
        
        return {
            "predicted_sleep_minutes": prediction_minutes,
            "predicted_sleep_formatted": f"{hours}h {minutes}m",
            "feature_importance": feature_importance,
            "input_features": input_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )

@router.get("/health")
async def ml_health_check():
    """Check if ML pipeline is available"""
    pipeline = load_pipeline()
    if pipeline is None:
        return {
            "status": "unavailable",
            "message": "ML pipeline not loaded",
            "path": PIPELINE_PATH
        }
    return {
        "status": "available",
        "message": "ML pipeline is ready",
        "model_type": str(type(pipeline.named_steps['model']))
    }

