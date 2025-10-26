#!/usr/bin/env python3
"""
Simple backend startup script with error handling
"""
import sys
import os
import uvicorn
from app.main import app

if __name__ == "__main__":
    print("🚀 Starting MindTrack Backend...")
    print("📍 Host: 0.0.0.0")
    print("📍 Port: 8000")
    print("📍 API Docs: http://localhost:8000/docs")
    print("=" * 50)
    
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)
