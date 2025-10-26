#!/usr/bin/env python3
"""
Simple server startup with detailed error handling
"""
import sys
import os
import traceback

def main():
    print("🚀 Starting MindTrack Backend...")
    print("📍 Current directory:", os.getcwd())
    print("📍 Python path:", sys.path[:3])
    
    try:
        print("\n1. Importing FastAPI...")
        from fastapi import FastAPI
        print("✅ FastAPI imported")
        
        print("\n2. Importing app...")
        from app.main import app
        print("✅ App imported successfully")
        
        print("\n3. Starting uvicorn...")
        import uvicorn
        
        print("📍 Host: 127.0.0.1")
        print("📍 Port: 8000")
        print("📍 API Docs: http://127.0.0.1:8000/docs")
        print("=" * 50)
        
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8000,
            log_level="info",
            reload=False
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("📍 Traceback:")
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"❌ Server error: {e}")
        print("📍 Traceback:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
