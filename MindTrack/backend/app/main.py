from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import logging
import os
import uvicorn
from sqlalchemy.orm import Session

from app.db.database import get_db, init_db, Base, engine
from app.models import User, DailyHabitEntry, Badge, Reminder, SensorSummary

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="MindTrack API",
    description="Habit tracking and wellness analytics API with ML predictions",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://mindtrack2-adm43bsyjgebtappztmcy2q.streamlit.app",  # Your Streamlit app domain
        "http://localhost:8501",  # Local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized successfully")

# Root endpoint
@app.get("/", tags=["root"])
async def root():
    return {
        "message": "MindTrack API is running",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "health": "/health"
        }
    }

# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check(db: Session = Depends(get_db)):
    try:
        # Test database connection with a simple query
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )

# Import and include routers
from app.routers import users, habits, badges, insights, ml_predictions

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(habits.router, prefix="/habits", tags=["habits"])
app.include_router(badges.router, prefix="/badges", tags=["badges"])
app.include_router(insights.router, prefix="/insights", tags=["insights"])
app.include_router(ml_predictions.router, prefix="/predictions", tags=["ml-predictions"])

def create_app():
    """Application factory for tests and external runners that expect a callable."""
    return app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )

