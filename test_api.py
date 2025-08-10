#!/usr/bin/env python3
"""
Test script for Facebook Browser API
"""

import requests
import json

# API Configuration
API_URL = "https://testingappbye.onrender.com"
NAVIGATE_ENDPOINT = f"{API_URL}/navigate"

def test_health_check():
    """Test if the API is healthy"""
    print("Testing health check...")
    response = requests.get(f"{API_URL}/health")
    if response.status_code == 200:
        print(f"✓ Health check passed: {response.json()}")
    else:
        print(f"✗ Health check failed: {response.status_code}")
    return response

def test_navigation(url):
    """Test navigation to a Facebook URL"""
    print(f"\nTesting navigation to: {url}")
    
    # Prepare the request
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "url": url
    }
    
    print(f"Sending POST request to {NAVIGATE_ENDPOINT}")
    print(f"Request data: {json.dumps(data, indent=2)}")
    
    try:
        # Send the request
        response = requests.post(NAVIGATE_ENDPOINT, 
                                  headers=headers, 
                                  json=data,
                                  timeout=30)
        
        # Check response
        if response.status_code == 200:
            result = response.json()
            print(f"\n✓ Navigation successful!")
            print(f"Response: {json.dumps(result, indent=2)}")
            return result
        else:
            print(f"\n✗ Navigation failed with status code: {response.status_code}")
            print(f"Error: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("\n✗ Request timed out (exceeded 30 seconds)")
        return None
    except Exception as e:
        print(f"\n✗ Error occurred: {e}")
        return None

def main():
    """Main test function"""
    print("=" * 60)
    print("Facebook Browser API Test")
    print("=" * 60)
    
    # Test health check
    test_health_check()
    
    # Test URLs
    test_urls = [
        "https://www.facebook.com/abestoflife",  # Your requested URL
        "facebook.com/marketplace",               # Marketplace example
        "zuck"                                     # Short URL example (will become facebook.com/zuck)
    ]
    
    # Test each URL
    for url in test_urls:
        test_navigation(url)
        print("-" * 60)

if __name__ == "__main__":
    main()
