#!/usr/bin/env python3
"""
Start both backend and frontend services
"""
import subprocess
import time
import sys
import os
import threading
import requests

def start_backend():
    """Start the backend server"""
    print("🚀 Starting Backend...")
    os.chdir("backend")
    try:
        subprocess.run([
            sys.executable, "-c", 
            "from app.main import app; import uvicorn; uvicorn.run(app, host='127.0.0.1', port=8000)"
        ], check=True)
    except Exception as e:
        print(f"❌ Backend error: {e}")

def start_frontend():
    """Start the frontend server"""
    print("🚀 Starting Frontend...")
    os.chdir("../frontend/MindTracker_frontend")
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py", 
            "--server.port", "8501", "--server.address", "127.0.0.1"
        ], check=True)
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

if __name__ == "__main__":
    print("🚀 Starting MindTrack Services...")
    print("=" * 50)
    
    # Start backend in a thread
    backend_thread = threading.Thread(target=start_backend)
    backend_thread.daemon = True
    backend_thread.start()
    
    # Wait a bit for backend to start
    time.sleep(3)
    
    # Start frontend in a thread
    frontend_thread = threading.Thread(target=start_frontend)
    frontend_thread.daemon = True
    frontend_thread.start()
    
    # Wait for services to start
    time.sleep(5)
    
    # Test services
    test_services()
    
    print("\n" + "=" * 50)
    print("🎉 Services started!")
    print("📍 Backend: http://127.0.0.1:8000")
    print("📍 Frontend: http://127.0.0.1:8501")
    print("📍 API Docs: http://127.0.0.1:8000/docs")
    print("\nPress Ctrl+C to stop all services")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        sys.exit(0)
