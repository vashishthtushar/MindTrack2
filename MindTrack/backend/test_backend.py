#!/usr/bin/env python3
"""
Test script to verify backend functionality
"""
import requests
import json
import time
import sys

def test_backend():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing MindTrack Backend...")
    print("=" * 50)
    
    # Test 1: Health check
    try:
        print("1. Testing root endpoint...")
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Root endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False
    
    # Test 2: Health check
    try:
        print("\n2. Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test 3: Create user
    try:
        print("\n3. Testing user creation...")
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
    
    # Test 4: List users
    try:
        print("\n4. Testing user listing...")
        response = requests.get(f"{base_url}/users/", timeout=5)
        if response.status_code == 200:
            print("✅ User listing working")
            users = response.json()
            print(f"   Found {len(users)} users")
        else:
            print(f"❌ User listing failed: {response.status_code}")
    except Exception as e:
        print(f"❌ User listing error: {e}")
    
    # Test 5: ML Health check
    try:
        print("\n5. Testing ML endpoint...")
        response = requests.get(f"{base_url}/predictions/health", timeout=5)
        if response.status_code == 200:
            print("✅ ML endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ ML endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ ML endpoint error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Backend testing completed!")
    return True

if __name__ == "__main__":
    print("Starting backend test...")
    time.sleep(2)  # Give server time to start
    test_backend()
