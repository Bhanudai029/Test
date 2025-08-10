#!/usr/bin/env python3
"""
Simple test script for Facebook Browser API
"""

import requests
import json
import sys
import time
import threading
from collections import defaultdict

def format_time(seconds):
    """Format time in a human-readable way"""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.1f}s"

class DynamicTimer:
    """A class to handle dynamic timer display"""
    def __init__(self, name, emoji="⏳"):
        self.name = name
        self.emoji = emoji
        self.start_time = None
        self.running = False
        self.timer_thread = None
        
    def start(self):
        """Start the dynamic timer"""
        self.start_time = time.time()
        self.running = True
        self.timer_thread = threading.Thread(target=self._update_timer, daemon=True)
        self.timer_thread.start()
        
    def stop(self):
        """Stop the dynamic timer and return elapsed time"""
        self.running = False
        if self.start_time:
            return time.time() - self.start_time
        return 0
        
    def _update_timer(self):
        """Update timer display every second"""
        while self.running:
            if self.start_time:
                elapsed = time.time() - self.start_time
                # Clear the line and print updated timer
                print(f"\r   {self.emoji} Testing {self.name}({int(elapsed)}s)", end="", flush=True)
                time.sleep(1)
            else:
                break
                
def make_request_with_timer(name, emoji, request_func):
    """Make a request with dynamic timer display"""
    timer = DynamicTimer(name, emoji)
    timer.start()
    
    try:
        result = request_func()
        duration = timer.stop()
        # Clear the timer line and show final result
        print(f"\r   {emoji} Testing {name}... DONE ({format_time(duration)})")
        return result, duration
    except Exception as e:
        duration = timer.stop()
        print(f"\r   {emoji} Testing {name}... FAILED ({format_time(duration)})")
        raise e

def test_api(base_url):
    """Test the API with all endpoints and timing"""
    
    # Track timing data
    timing_data = defaultdict(list)
    total_start_time = time.time()
    
    print(f"\n{'='*80}")
    print("🚀 FACEBOOK BROWSER API PERFORMANCE TEST")
    print(f"{'='*80}")
    print(f"Testing: {base_url}")
    print(f"Started at: {time.strftime('%H:%M:%S')}\n")
    
    # Test 1: Health Check
    print("1. 🏥 Testing /health endpoint...")
    start_time = time.time()
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        end_time = time.time()
        duration = end_time - start_time
        timing_data['health'].append(duration)
        
        if response.status_code == 200:
            print(f"   ✅ Health check passed: {response.json()}")
            print(f"   ⏱️  Response time: {format_time(duration)}")
        else:
            print(f"   ❌ Health check failed: Status {response.status_code}")
            print(f"   ⏱️  Response time: {format_time(duration)}")
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        print(f"   ❌ Health check error: {e}")
        print(f"   ⏱️  Failed after: {format_time(duration)}")
        print("\n⚠️  API not reachable. Is the server running?")
        return False
    
    # Test 2: GET endpoints
    test_cases = [
        ("zuck", "/api/visit/zuck", "👤"),
        ("marketplace", "/api/visit/marketplace", "🛒"),
        ("abestoflife", "/api/visit/abestoflife", "📖")
    ]
    
    print("\n2. 🔗 Testing GET /api/visit/{username} endpoints...")
    successful_requests = 0
    total_get_requests = len(test_cases)
    
    for name, endpoint, emoji in test_cases:
        print()  # Add spacing
        
        def make_request():
            return requests.get(f"{base_url}{endpoint}", timeout=60)
        
        try:
            response, duration = make_request_with_timer(name, emoji, make_request)
            timing_data[f'get_{name}'].append(duration)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"      ✅ SUCCESS")
                    print(f"      🔗 Initial: {data.get('initial_url')}")
                    print(f"      🎯 Final:   {data.get('final_url')}")
                    if 'photo' in data.get('final_url', '') and 'fbid' in data.get('final_url', ''):
                        print(f"      📸 Photo URL detected!")
                    successful_requests += 1
                else:
                    print(f"      ❌ Failed: {data.get('error')}")
            else:
                print(f"      ❌ Error: Status {response.status_code}")
                print(f"      📄 {response.text[:100]}")
        except requests.exceptions.Timeout:
            print(f"      ⏱️  Request timed out")
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    # Test 3: POST endpoint
    print("\n3. 📤 Testing POST /navigate endpoint...")
    print()  # Add spacing
    
    def make_post_request():
        return requests.post(
            f"{base_url}/navigate",
            json={"url": "facebook.com/zuck"},
            headers={"Content-Type": "application/json"},
            timeout=60
        )
    
    try:
        response, duration = make_request_with_timer("navigate", "📤", make_post_request)
        timing_data['post_navigate'].append(duration)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"      ✅ POST endpoint works")
            else:
                print(f"      ❌ Failed: {data.get('error')}")
        else:
            print(f"      ❌ Error: Status {response.status_code}")
    except Exception as e:
        print(f"      ❌ Error: {e}")
    
    # Calculate and display timing summary
    total_end_time = time.time()
    total_duration = total_end_time - total_start_time
    
    print(f"\n{'='*80}")
    print("⏱️  PERFORMANCE SUMMARY")
    print(f"{'='*80}")
    print(f"Total test duration: {format_time(total_duration)}")
    print(f"Successful GET requests: {successful_requests}/{total_get_requests}")
    print(f"Test completed at: {time.strftime('%H:%M:%S')}")
    
    # Show average times for each endpoint type
    if timing_data:
        print("\n📊 Average Response Times:")
        print("-" * 50)
        
        for endpoint, times in timing_data.items():
            if times:
                avg_time = sum(times) / len(times)
                min_time = min(times)
                max_time = max(times)
                
                endpoint_name = endpoint.replace('_', ' ').title()
                print(f"   {endpoint_name}:")
                print(f"      Average: {format_time(avg_time)}")
                print(f"      Fastest: {format_time(min_time)}")
                print(f"      Slowest: {format_time(max_time)}")
                print(f"      Requests: {len(times)}")
                print()
        
        # Calculate overall average for GET requests
        all_get_times = []
        for key, times in timing_data.items():
            if key.startswith('get_'):
                all_get_times.extend(times)
        
        if all_get_times:
            overall_avg = sum(all_get_times) / len(all_get_times)
            print(f"🎯 Overall GET Average: {format_time(overall_avg)} per request")
            
            if len(all_get_times) > 1:
                estimated_time_per_request = overall_avg
                print(f"📈 Estimated time for 1 request: ~{format_time(estimated_time_per_request)}")
    
    print(f"\n{'='*80}")
    print("🏁 Test complete!")
    print(f"{'='*80}")
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
