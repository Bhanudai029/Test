#!/usr/bin/env python3
"""
Simple test script for Facebook Browser API
"""

import requests
import json
import sys

def test_api(base_url):
    """Test the API with all endpoints"""
    
    print(f"\n{'='*60}")
    print("FACEBOOK BROWSER API TEST")
    print(f"{'='*60}")
    print(f"Testing: {base_url}\n")
    
    # Test 1: Health Check
    print("1. Testing /health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print(f"   ✅ Health check passed: {response.json()}")
        else:
            print(f"   ❌ Health check failed: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        print("\n⚠️  API not reachable. Is the server running?")
        return False
    
    # Test 2: GET endpoints
    test_cases = [
        ("zuck", "/api/visit/zuck"),
        ("marketplace", "/api/visit/marketplace"),
        ("abestoflife", "/api/visit/abestoflife")
    ]
    
    print("\n2. Testing GET /api/visit/{username} endpoints...")
    for name, endpoint in test_cases:
        print(f"\n   Testing {name}...")
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"   ✅ SUCCESS")
                    print(f"      Initial: {data.get('initial_url')}")
                    print(f"      Final:   {data.get('final_url')}")
                    if 'photo' in data.get('final_url', '') and 'fbid' in data.get('final_url', ''):
                        print(f"      🎯 Photo URL detected!")
                else:
                    print(f"   ❌ Failed: {data.get('error')}")
            else:
                print(f"   ❌ Error: Status {response.status_code}")
                print(f"      {response.text[:100]}")
        except requests.exceptions.Timeout:
            print(f"   ⏱️ Request timed out")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test 3: POST endpoint
    print("\n3. Testing POST /navigate endpoint...")
    try:
        response = requests.post(
            f"{base_url}/navigate",
            json={"url": "facebook.com/zuck"},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   ✅ POST endpoint works")
            else:
                print(f"   ❌ Failed: {data.get('error')}")
        else:
            print(f"   ❌ Error: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print(f"\n{'='*60}")
    print("Test complete!")
    return True

if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        # Try to find a working server
        urls_to_try = [
            "http://localhost:10000",
            "https://facebook-browser-lite.onrender.com",
            "https://facebook-victory-14.onrender.com"
        ]
        
        url = None
        for test_url in urls_to_try:
            try:
                print(f"Checking {test_url}...")
                response = requests.get(f"{test_url}/health", timeout=3)
                if response.status_code == 200:
                    url = test_url
                    break
            except:
                continue
        
        if not url:
            print("\n❌ No API server found!")
            print("\nUsage:")
            print("  python test.py                    # Auto-detect server")
            print("  python test.py http://localhost:10000  # Test local server")
            print("  python test.py https://your-app.onrender.com  # Test deployed server")
            print("\nMake sure your server is running:")
            print("  python app.py")
            sys.exit(1)
    
    test_api(url)
