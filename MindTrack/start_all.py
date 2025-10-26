#!/usr/bin/env python3
"""
Start both backend and frontend with proper error handling
"""
import subprocess
import time
import sys
import os
import threading
import requests
from pathlib import Path

def start_backend():
    """Start the backend server"""
    print("🚀 Starting Backend...")
    backend_dir = Path("backend")
    os.chdir(backend_dir)
    
    try:
        # Start backend with proper error handling
        result = subprocess.run([
            sys.executable, "-c", 
            "from app.main import app; import uvicorn; print('Backend starting...'); uvicorn.run(app, host='127.0.0.1', port=8000, log_level='info')"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            print(f"❌ Backend error: {result.stderr}")
        else:
            print("✅ Backend started successfully")
            
    except subprocess.TimeoutExpired:
        print("⏰ Backend startup timed out")
    except Exception as e:
        print(f"❌ Backend error: {e}")

def start_frontend():
    """Start the frontend server"""
    print("🚀 Starting Frontend...")
    frontend_dir = Path("../frontend/MindTracker_frontend")
    os.chdir(frontend_dir)
    
    try:
        # Start frontend with proper error handling
        result = subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py", 
            "--server.port", "8501", "--server.address", "127.0.0.1",
            "--server.headless", "true"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            print(f"❌ Frontend error: {result.stderr}")
        else:
            print("✅ Frontend started successfully")
            
    except subprocess.TimeoutExpired:
        print("⏰ Frontend startup timed out")
    except Exception as e:
        print(f"❌ Frontend error: {e}")

def test_services():
    """Test if services are running"""
    print("\n🧪 Testing Services...")
    
    # Test backend
    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running at http://127.0.0.1:8000")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Backend error: {response.status_code}")
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
    
    # Test frontend
    try:
        response = requests.get("http://127.0.0.1:8501/", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is running at http://127.0.0.1:8501")
        else:
            print(f"❌ Frontend error: {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend not accessible: {e}")

def main():
    print("🚀 Starting MindTrack Services...")
    print("=" * 50)
    
    # Start backend in a thread
    backend_thread = threading.Thread(target=start_backend)
    backend_thread.daemon = True
    backend_thread.start()
    
    # Wait for backend to start
    print("⏳ Waiting for backend to start...")
    time.sleep(5)
    
    # Test backend first
    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is working!")
            
            # Now start frontend
            frontend_thread = threading.Thread(target=start_frontend)
            frontend_thread.daemon = True
            frontend_thread.start()
            
            # Wait for frontend
            time.sleep(5)
            
            # Test both services
            test_services()
            
        else:
            print("❌ Backend failed to start")
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Services startup completed!")
    print("📍 Backend: http://127.0.0.1:8000")
    print("📍 Frontend: http://127.0.0.1:8501")
    print("📍 API Docs: http://127.0.0.1:8000/docs")

if __name__ == "__main__":
    main()
