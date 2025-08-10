#!/usr/bin/env python3
"""
Lightweight Facebook Browser API for Render deployment
Provides a simple web interface for headless browser navigation
"""

from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
import time
import os
import threading
import subprocess
import platform

app = Flask(__name__)

# Global driver instance for reuse (lightweight approach)
driver_instance = None
driver_lock = threading.Lock()

def get_chrome_options():
    """Configure lightweight Chrome options for Render deployment"""
    chrome_options = Options()
    
    # Headless mode is required for Render
    chrome_options.add_argument("--headless=new")  # Use new headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")  # Don't load images to save memory
    
    # Aggressive memory optimization
    chrome_options.add_argument("--memory-pressure-off")
    chrome_options.add_argument("--max_old_space_size=256")  # Reduced from 512
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    chrome_options.add_argument("--disable-features=TranslateUI")
    chrome_options.add_argument("--disable-ipc-flooding-protection")
    chrome_options.add_argument("--single-process")  # Run in single process to save memory
    chrome_options.add_argument("--disable-setuid-sandbox")
    
    # Set minimal window size
    chrome_options.add_argument("--window-size=800,600")  # Smaller window
    
    # User agent
    chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    return chrome_options

def verify_chromedriver():
    """Verify ChromeDriver installation and return path"""
    # Check system installation first
    chromedriver_path = "/usr/bin/chromedriver"
    
    if os.path.exists(chromedriver_path):
        try:
            # Test if it's actually executable
            result = subprocess.run([chromedriver_path, "--version"], 
                                    capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"ChromeDriver found and working: {result.stdout.strip()}")
                return chromedriver_path
            else:
                print(f"ChromeDriver exists but failed: {result.stderr}")
        except Exception as e:
            print(f"Error testing ChromeDriver: {e}")
    
    # Try alternative location
    chromedriver_path = "/usr/local/bin/chromedriver"
    if os.path.exists(chromedriver_path):
        print(f"Found ChromeDriver at alternative location: {chromedriver_path}")
        return chromedriver_path
    
    # For local Windows development
    if platform.system() == "Windows":
        for path in ["chromedriver.exe", "chromedriver"]:
            if os.path.exists(path):
                print(f"Found ChromeDriver for Windows: {path}")
                return path
    
    print("ChromeDriver not found in any expected location")
    return None

def get_or_create_driver():
    """Get existing driver or create new one (singleton pattern for efficiency)"""
    global driver_instance
    
    with driver_lock:
        if driver_instance is None:
            try:
                # Verify ChromeDriver first
                chromedriver_path = verify_chromedriver()
                if not chromedriver_path:
                    raise Exception("ChromeDriver not found or not working")
                
                chrome_options = get_chrome_options()
                
                print(f"Initializing Chrome with driver at: {chromedriver_path}")
                service = Service(executable_path=chromedriver_path)
                
                driver_instance = webdriver.Chrome(service=service, options=chrome_options)
                print("Successfully created Chrome driver instance")
            except Exception as e:
                print(f"Error creating driver: {e}")
                import traceback
                print(f"Full traceback:\n{traceback.format_exc()}")
                return None
        return driver_instance

def navigate_and_interact(url):
    """Navigate to Facebook URL and perform automated interactions"""
    driver = get_or_create_driver()
    if not driver:
        return None, "Failed to initialize browser"
    
    try:
        # Ensure URL is properly formatted
        if not url.startswith('http'):
            if 'facebook.com' in url:
                url = 'https://' + url
            else:
                url = 'https://www.facebook.com/' + url.lstrip('/')
        
        # Navigate to URL
        driver.get(url)
        
        # Wait 2 seconds
        time.sleep(2)
        
        # Perform key sequence
        actions = ActionChains(driver)
        
        # Press Escape
        actions.send_keys(Keys.ESCAPE).perform()
        time.sleep(0.5)
        
        # Press Tab 7 times
        for _ in range(7):
            actions.send_keys(Keys.TAB).perform()
            time.sleep(0.2)
        
        # Press Enter
        actions.send_keys(Keys.ENTER).perform()
        
        # Wait for page changes
        time.sleep(2)
        
        # Get final URL and title
        final_url = driver.current_url
        page_title = driver.title
        
        return {
            'success': True,
            'initial_url': url,
            'final_url': final_url,
            'page_title': page_title
        }, None
        
    except Exception as e:
        return None, str(e)

@app.route('/')
def home():
    """Simple home page with API instructions"""
    return '''
    <html>
        <head><title>Facebook Browser API</title></head>
        <body style="font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px;">
            <h1>🌐 Lightweight Facebook Browser API</h1>
            <p>This service provides headless browser navigation for Facebook URLs.</p>
            
            <h2>API Usage:</h2>
            <pre style="background: #f4f4f4; padding: 15px; border-radius: 5px;">
POST /navigate
Content-Type: application/json

{
    "url": "facebook.com/marketplace"
}
            </pre>
            
            <h2>Response:</h2>
            <pre style="background: #f4f4f4; padding: 15px; border-radius: 5px;">
{
    "success": true,
    "initial_url": "https://www.facebook.com/marketplace",
    "final_url": "https://www.facebook.com/...",
    "page_title": "Facebook - Marketplace"
}
            </pre>
            
            <h2>Health Check:</h2>
            <p>GET /health - Check if service is running</p>
        </body>
    </html>
    '''

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'facebook-browser'})

@app.route('/navigate', methods=['POST'])
def navigate():
    """Navigate to Facebook URL and perform automated actions"""
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        url = data['url']
        result, error = navigate_and_interact(url)
        
        if error:
            return jsonify({'error': error}), 500
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/shutdown', methods=['POST'])
def shutdown():
    """Gracefully shutdown the browser instance"""
    global driver_instance
    
    with driver_lock:
        if driver_instance:
            try:
                driver_instance.quit()
                driver_instance = None
                return jsonify({'status': 'Browser instance closed'})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        return jsonify({'status': 'No browser instance to close'})

# Verify ChromeDriver on startup
print("Starting Facebook Browser API...")
print(f"Python version: {platform.python_version()}")
print(f"Platform: {platform.system()} {platform.release()}")

# Check ChromeDriver availability
chromedriver_check = verify_chromedriver()
if chromedriver_check:
    print(f"✓ ChromeDriver verified at: {chromedriver_check}")
else:
    print("✗ WARNING: ChromeDriver not found or not working!")
    print("The service will start but browser operations will fail.")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
