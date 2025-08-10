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
import traceback

app = Flask(__name__)

# Global driver instance for reuse (lightweight approach)
driver_instance = None
driver_lock = threading.Lock()

def get_chrome_options():
    """Configure lightweight Chrome options for Render deployment"""
    chrome_options = Options()
    
    # Check for Chrome binary in multiple locations
    chrome_binaries = [
        "/usr/bin/google-chrome-stable",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium-browser",
        "/usr/bin/chromium"
    ]
    
    chrome_binary = None
    for binary in chrome_binaries:
        if os.path.exists(binary):
            chrome_binary = binary
            print(f"Found Chrome binary at: {chrome_binary}")
            try:
                result = subprocess.run([binary, "--version"], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print(f"Chrome version: {result.stdout.strip()}")
            except Exception as e:
                print(f"Error checking Chrome version: {e}")
            break
    
    if chrome_binary:
        chrome_options.binary_location = chrome_binary
    else:
        print("WARNING: Chrome binary not found in expected locations")
        # Try to find it in PATH
        try:
            result = subprocess.run(["which", "google-chrome"], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                chrome_binary = result.stdout.strip()
                chrome_options.binary_location = chrome_binary
                print(f"Found Chrome in PATH at: {chrome_binary}")
        except:
            pass
    
    # Essential headless configuration
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-setuid-sandbox")
    
    # Performance and stability
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")  # Don't load images to save memory
    
    # Memory optimization (without single-process which can cause issues)
    chrome_options.add_argument("--memory-pressure-off")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    chrome_options.add_argument("--disable-features=TranslateUI")
    chrome_options.add_argument("--disable-ipc-flooding-protection")
    
    # Additional stability options
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--disable-dev-tools")
    
    # Set window size
    chrome_options.add_argument("--window-size=1280,720")
    
    # User agent
    chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
    
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
                # Set reasonable timeouts
                driver_instance.set_page_load_timeout(25)  # 25 seconds for page load
                driver_instance.implicitly_wait(5)  # 5 seconds implicit wait (reduced from 10)
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
        
        print(f"Navigating to: {url}")
        
        # Set page load timeout to 20 seconds (to avoid 30s timeout)
        driver.set_page_load_timeout(20)
        
        try:
            # Navigate to URL
            driver.get(url)
        except:
            # If page load times out, continue anyway as page might be partially loaded
            print("Page load timeout, continuing with interaction...")
            pass
        
        # Wait 2 seconds for initial page load
        time.sleep(2)
        
        # Perform key sequence
        actions = ActionChains(driver)
        
        # Press Escape to close any popups
        print("Pressing Escape...")
        actions.send_keys(Keys.ESCAPE).perform()
        time.sleep(0.5)
        
        # Press Tab 7 times to navigate to the target element
        print("Pressing Tab 7 times...")
        for i in range(7):
            actions.send_keys(Keys.TAB).perform()
            time.sleep(0.2)  # Small delay between tabs
        
        # Press Enter to activate the element
        print("Pressing Enter...")
        actions.send_keys(Keys.ENTER).perform()
        
        # Wait for navigation/page changes
        time.sleep(3)  # Increased wait time
        
        # Get final URL and title
        final_url = driver.current_url
        page_title = driver.title
        
        print(f"Final URL: {final_url}")
        print(f"Page title: {page_title}")
        
        # Check if we got a photo URL format
        if "photo" in final_url and "fbid" in final_url:
            print("Successfully navigated to photo URL")
        
        return {
            'success': True,
            'initial_url': url,
            'final_url': final_url,
            'page_title': page_title
        }, None
        
    except Exception as e:
        print(f"Error during navigation: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
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

@app.route('/diagnostics')
def diagnostics():
    """Diagnostics endpoint to check system status"""
    diagnostics_info = {
        'platform': platform.system(),
        'python_version': platform.python_version(),
        'chromedriver_check': None,
        'chrome_check': None,
        'environment': {
            'PORT': os.environ.get('PORT'),
            'RENDER': os.environ.get('RENDER', 'false'),
        }
    }
    
    # Check ChromeDriver
    chromedriver_path = verify_chromedriver()
    if chromedriver_path:
        diagnostics_info['chromedriver_check'] = {
            'status': 'found',
            'path': chromedriver_path
        }
    else:
        diagnostics_info['chromedriver_check'] = {
            'status': 'not_found',
            'error': 'ChromeDriver not found or not working'
        }
    
    # Check Chrome
    try:
        chrome_result = subprocess.run(['google-chrome', '--version'], 
                                      capture_output=True, text=True, timeout=5)
        if chrome_result.returncode == 0:
            diagnostics_info['chrome_check'] = {
                'status': 'found',
                'version': chrome_result.stdout.strip()
            }
        else:
            diagnostics_info['chrome_check'] = {
                'status': 'error',
                'error': chrome_result.stderr
            }
    except FileNotFoundError:
        diagnostics_info['chrome_check'] = {
            'status': 'not_found',
            'error': 'Chrome not found'
        }
    except Exception as e:
        diagnostics_info['chrome_check'] = {
            'status': 'error',
            'error': str(e)
        }
    
    # Try to create a test driver
    test_driver_result = {'status': 'not_tested', 'error': None}
    try:
        chrome_options = get_chrome_options()
        if chromedriver_path:
            service = Service(executable_path=chromedriver_path)
            test_driver = webdriver.Chrome(service=service, options=chrome_options)
            test_driver.quit()
            test_driver_result['status'] = 'success'
    except Exception as e:
        test_driver_result['status'] = 'failed'
        test_driver_result['error'] = str(e)
        test_driver_result['traceback'] = traceback.format_exc()
    
    diagnostics_info['test_driver'] = test_driver_result
    
    return jsonify(diagnostics_info)

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
