#!/usr/bin/env python3
"""
Single URL test for Facebook Browser API
"""

import requests
import json
import sys

# API endpoint
API_URL = "https://testingappbye.onrender.com"

def test_single_url(url):
    """Test a single URL"""
    print(f"\nTesting: {url}")
    print("=" * 60)
    
    # Test navigation
    try:
        print(f"Sending POST request to {API_URL}/navigate")
        response = requests.post(
            f"{API_URL}/navigate",
            json={"url": url},
            timeout=35  # 35 second timeout
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Navigation successful!")
            print(f"Initial URL: {data.get('initial_url')}")
            print(f"Final URL: {data.get('final_url')}")
            print(f"Page Title: {data.get('page_title')}")
            
            # Check if it's a photo URL
            final_url = data.get('final_url', '')
            if 'photo' in final_url and 'fbid' in final_url:
                print("✓ Successfully redirected to photo URL!")
            else:
                print("⚠ Did not redirect to photo URL")
        else:
            print(f"✗ Navigation failed with status code: {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.Timeout:
        print("✗ Request timed out (exceeded 35 seconds)")
    except Exception as e:
        print(f"✗ Error: {e}")

def shutdown_browser():
    """Shutdown the browser instance"""
    print("\nShutting down browser instance...")
    try:
        response = requests.post(f"{API_URL}/shutdown", timeout=10)
        if response.status_code == 200:
            print("✓ Browser shutdown successful")
        else:
            print(f"Browser shutdown returned: {response.text}")
    except Exception as e:
        print(f"Error shutting down browser: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        # Default test URL
        url = "zuck"
    
    # First shutdown any existing browser
    shutdown_browser()
    
    # Test the URL
    test_single_url(url)
    
    # Shutdown browser after test
    shutdown_browser()
