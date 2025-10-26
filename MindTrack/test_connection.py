#!/usr/bin/env python3
"""
Test the connection between frontend and backend
"""
import requests
import json
import time

def test_backend():
    """Test backend functionality"""
    print("🧪 Testing Backend...")
    
    base_url = "http://127.0.0.1:8000"
    
    # Test 1: Root endpoint
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Backend root endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Backend root failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        return False
    
    # Test 2: Health check
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend health check working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Backend health check error: {e}")
    
    # Test 3: Create user
    try:
        user_data = {
            "name": "Test User",
            "timezone": "UTC",
            "preferences": {}
        }
        response = requests.post(f"{base_url}/users/", json=user_data, timeout=5)
        if response.status_code == 201:
            print("✅ User creation working")
            user_info = response.json()
            print(f"   User ID: {user_info.get('user_id')}")
            return user_info.get('user_id')
        else:
            print(f"❌ User creation failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ User creation error: {e}")
    
    return None

def test_frontend_api():
    """Test frontend API client"""
    print("\n🧪 Testing Frontend API Client...")
    
    try:
        # Import the API client
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), "frontend", "MindTracker_frontend"))
        
        from utils.api import api
        
        # Test creating a user
        user_data = api.create_user(name="Frontend Test User", timezone="UTC")
        print("✅ Frontend API client working")
        print(f"   Created user: {user_data}")
        return user_data.get('user_id')
        
    except Exception as e:
        print(f"❌ Frontend API client error: {e}")
        return None

def main():
    print("🚀 Testing MindTrack Connection...")
    print("=" * 50)
    
    # Test backend
    user_id = test_backend()
    
    if user_id:
        print(f"\n✅ Backend is working! User ID: {user_id}")
        
        # Test frontend API client
        frontend_user_id = test_frontend_api()
        
        if frontend_user_id:
            print(f"\n✅ Frontend API client is working! User ID: {frontend_user_id}")
            print("\n🎉 Both backend and frontend are working correctly!")
        else:
            print("\n⚠️ Backend is working but frontend API client has issues")
    else:
        print("\n❌ Backend is not working properly")
    
    print("\n" + "=" * 50)
    print("📍 Backend API: http://127.0.0.1:8000")
    print("📍 API Documentation: http://127.0.0.1:8000/docs")
    print("📍 Frontend: http://127.0.0.1:8501 (if running)")

if __name__ == "__main__":
    main()
