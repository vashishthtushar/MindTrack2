#!/usr/bin/env python3
"""
Test script to verify backend functionality
"""
import requests
import json
import time

def test_backend():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing MindTrack Backend...")
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Root endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False
    
    # Test 2: Create user
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
        return False
    
    return None

if __name__ == "__main__":
    print("Starting backend test...")
    time.sleep(2)  # Give server time to start
    test_backend()
