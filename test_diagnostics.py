#!/usr/bin/env python3
"""
Diagnostics test for Facebook Browser API
"""

import requests
import json
import time

API_URL = "https://testingappbye.onrender.com"

def test_diagnostics():
    """Test the diagnostics endpoint"""
    print("=" * 60)
    print("Facebook Browser API - Diagnostics Test")
    print("=" * 60)
    
    # Wait a moment for deployment
    print("\nChecking if service is deployed...")
    
    # First check health
    try:
        health_response = requests.get(f"{API_URL}/health", timeout=10)
        if health_response.status_code == 200:
            print("✓ Service is running")
        else:
            print("✗ Service health check failed")
            return
    except Exception as e:
        print(f"✗ Service not reachable: {e}")
        print("The service might still be deploying. Please wait and try again.")
        return
    
    # Now run diagnostics
    print("\nRunning diagnostics...")
    try:
        response = requests.get(f"{API_URL}/diagnostics", timeout=30)
        
        if response.status_code == 200:
            diagnostics = response.json()
            
            print("\n" + "=" * 40)
            print("DIAGNOSTICS RESULTS")
            print("=" * 40)
            
            # Platform info
            print(f"\n📍 Platform: {diagnostics.get('platform')}")
            print(f"🐍 Python: {diagnostics.get('python_version')}")
            
            # Environment
            env = diagnostics.get('environment', {})
            print(f"\n🌍 Environment:")
            print(f"   PORT: {env.get('PORT')}")
            print(f"   RENDER: {env.get('RENDER')}")
            
            # ChromeDriver check
            chromedriver = diagnostics.get('chromedriver_check', {})
            print(f"\n🔧 ChromeDriver:")
            if chromedriver.get('status') == 'found':
                print(f"   ✓ Status: Found")
                print(f"   📂 Path: {chromedriver.get('path')}")
            else:
                print(f"   ✗ Status: {chromedriver.get('status')}")
                print(f"   ❌ Error: {chromedriver.get('error')}")
            
            # Chrome check
            chrome = diagnostics.get('chrome_check', {})
            print(f"\n🌐 Chrome Browser:")
            if chrome.get('status') == 'found':
                print(f"   ✓ Status: Found")
                print(f"   📦 Version: {chrome.get('version')}")
            else:
                print(f"   ✗ Status: {chrome.get('status')}")
                print(f"   ❌ Error: {chrome.get('error')}")
            
            # Test driver
            test_driver = diagnostics.get('test_driver', {})
            print(f"\n🚗 Test Driver Creation:")
            if test_driver.get('status') == 'success':
                print(f"   ✓ Status: Success - Chrome driver can be created!")
            else:
                print(f"   ✗ Status: {test_driver.get('status')}")
                if test_driver.get('error'):
                    print(f"   ❌ Error: {test_driver.get('error')}")
                if test_driver.get('traceback'):
                    print(f"\n   📋 Traceback:")
                    print("   " + "\n   ".join(test_driver.get('traceback').split('\n')))
            
            print("\n" + "=" * 40)
            
            # Save full diagnostics to file
            with open('diagnostics_result.json', 'w') as f:
                json.dump(diagnostics, f, indent=2)
            print("\n💾 Full diagnostics saved to: diagnostics_result.json")
            
        else:
            print(f"✗ Diagnostics endpoint returned status: {response.status_code}")
            print(f"Response: {response.text}")
    
    except requests.exceptions.RequestException as e:
        print(f"✗ Error calling diagnostics: {e}")

if __name__ == "__main__":
    test_diagnostics()
