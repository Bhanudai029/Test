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
import re
from urllib.parse import urlparse, urlunparse, parse_qs

# Optional: webdriver-manager to auto-download ChromeDriver when not present
try:
    from webdriver_manager.chrome import ChromeDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except Exception:
    ChromeDriverManager = None
    WEBDRIVER_MANAGER_AVAILABLE = False

app = Flask(__name__)

# Global driver instance for reuse (lightweight approach)
driver_instance = None
driver_lock = threading.Lock()

def get_chrome_options(is_headless: bool | None = None):
    """Configure lightweight Chrome options for Render deployment.
    If is_headless is None, use HEADLESS env; otherwise honor the override.
    """
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
    
    # Essential headless configuration (toggle via HEADLESS env or override)
    if is_headless is None:
        headless_env = os.environ.get("HEADLESS", "true").lower()
        is_headless = headless_env not in ("0", "false", "no")
    if is_headless:
        chrome_options.add_argument("--headless=new")
    else:
        print("HEADLESS disabled; launching Chrome in headed mode")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-setuid-sandbox")
    
    # Performance and stability
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    # Avoid disabling images when running headed so user can see the page fully
    if is_headless:
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
    if not is_headless:
        chrome_options.add_argument("--start-maximized")
    
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
    
    # Attempt to locate chromedriver on PATH
    for cmd in ("chromedriver", "chromedriver.exe"):
        try:
            result = subprocess.run([cmd, "--version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"Found ChromeDriver on PATH via {cmd}: {result.stdout.strip()}")
                return cmd
        except Exception:
            pass

    # webdriver-manager fallback: try to download a compatible ChromeDriver
    if WEBDRIVER_MANAGER_AVAILABLE:
        try:
            print("Attempting to download ChromeDriver via webdriver-manager...")
            driver_path = download_with_webdriver_manager()
            if driver_path and os.path.exists(driver_path):
                print(f"Downloaded ChromeDriver to: {driver_path}")
                return driver_path
        except Exception as e:
            print(f"webdriver-manager failed to install ChromeDriver: {e}")

    print("ChromeDriver not found in any expected location")
    return None

# Helper to safely download ChromeDriver via webdriver-manager when available
def download_with_webdriver_manager():
    if not WEBDRIVER_MANAGER_AVAILABLE or ChromeDriverManager is None:
        return None
    try:
        print("Downloading ChromeDriver using webdriver-manager...")
        driver_path = ChromeDriverManager().install()
        return driver_path
    except Exception as e:
        print(f"webdriver-manager install failed: {e}")
        return None

def get_or_create_driver(is_headless: bool | None = None):
    """Create a new driver instance for each request. Honor headless override if provided."""
    try:
        # Verify ChromeDriver first; if not found, fall back to Selenium Manager
        chromedriver_path = verify_chromedriver()
        chrome_options = get_chrome_options(is_headless=is_headless)

        if chromedriver_path:
            print(f"Creating new Chrome instance with driver at: {chromedriver_path}")
            service = Service(executable_path=chromedriver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            # Try webdriver-manager first (preferred for reproducible installs)
            if WEBDRIVER_MANAGER_AVAILABLE:
                try:
                    print("Using webdriver-manager to install ChromeDriver and create driver...")
                    driver_path = download_with_webdriver_manager()
                    if driver_path:
                        service = Service(executable_path=driver_path)
                        driver = webdriver.Chrome(service=service, options=chrome_options)
                    else:
                        raise RuntimeError("webdriver-manager did not provide a driver path")
                except Exception as e:
                    print(f"webdriver-manager failed: {e}; falling back to Selenium Manager auto-resolution")
                    driver = webdriver.Chrome(options=chrome_options)
            else:
                print("ChromeDriver not found; attempting to use Selenium Manager fallback...")
                # Selenium Manager (built into Selenium) will attempt to download a driver when service is not provided
                driver = webdriver.Chrome(options=chrome_options)
        # Set reasonable timeouts
        driver.set_page_load_timeout(25)  # 25 seconds for page load
        driver.implicitly_wait(5)  # 5 seconds implicit wait
        print("Successfully created Chrome driver instance")
        return driver
    except Exception as e:
        print(f"Error creating driver: {e}")
        import traceback
        print(f"Full traceback:\n{traceback.format_exc()}")
        return None

def normalize_facebook_url(url: str) -> str:
    """Normalize Facebook URLs.
    - Ensure https scheme and www subdomain
    - Convert numeric path like /123456789 to /profile.php?id=123456789
    """
    # Ensure scheme and base
    if not url.startswith('http'):
        if 'facebook.com' in url:
            url = 'https://' + url.lstrip('/')
        else:
            url = 'https://www.facebook.com/' + url.lstrip('/')

    p = urlparse(url)

    # Normalize domain to www.facebook.com for consistency
    netloc = p.netloc
    if netloc.endswith('facebook.com') and not netloc.startswith('www.'):
        netloc = 'www.facebook.com'

    path = p.path or '/'

    # If path is purely a numeric ID, rewrite to profile.php?id=...
    m = re.fullmatch(r'/(\d+)/?', path)
    if m:
        user_id = m.group(1)
        new_p = p._replace(netloc=netloc, path='/profile.php', query=f'id={user_id}')
        return urlunparse(new_p)

    # Otherwise just return with normalized netloc if it changed
    if netloc != p.netloc:
        p = p._replace(netloc=netloc)
        return urlunparse(p)
    return url

def navigate_and_interact(url, request_id=None, is_headless: bool | None = None):
    """Navigate to Facebook URL and perform automated interactions.
    If is_headless is provided, it overrides the default for this request.
    """
    import uuid
    request_id = request_id or str(uuid.uuid4())[:8]
    print(f"\n[{request_id}] Starting navigation request")
    
    driver = None
    try:
        driver = get_or_create_driver(is_headless=is_headless)
        if not driver:
            return None, "Failed to initialize browser"
        
        # Ensure URL is properly formatted and normalized
        url = normalize_facebook_url(url)

        print(f"[{request_id}] Navigating to: {url}")
        
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
        
        result = {
            'success': True,
            'initial_url': url,
            'final_url': final_url,
            'page_title': page_title
        }
        
        return result, None
        
    except Exception as e:
        print(f"Error during navigation: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return None, str(e)
    finally:
        # Always close the driver
        if driver:
            try:
                print("Closing browser instance...")
                driver.quit()
            except:
                pass

@app.route('/')
def home():
    """Simple home page with API instructions"""
    return '''
    <html>
        <head><title>Facebook Browser API</title></head>
        <body style="font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px;">
            <h1>🌐 Facebook Browser API</h1>
            <p>This service provides headless browser navigation for Facebook URLs.</p>
            
            <h2>Available Endpoints:</h2>
            
            <h3>1. Simple GET Endpoints (Easy to test):</h3>
            <pre style="background: #f4f4f4; padding: 15px; border-radius: 5px;">
GET /api/visit/{username}   - Visit a Facebook profile
GET /visit/{username}        - Alternative shorter URL

Examples:
  /api/visit/zuck          → Mark Zuckerberg's profile
  /api/visit/marketplace   → Facebook Marketplace
  /api/visit/abestoflife   → A Best of Life page
            </pre>
            
            <h3>2. POST Endpoint (More flexible):</h3>
            <pre style="background: #f4f4f4; padding: 15px; border-radius: 5px;">
POST /navigate
Content-Type: application/json

{
    "url": "facebook.com/marketplace"
}
            </pre>
            
            <h3>3. Utility Endpoints:</h3>
            <pre style="background: #f4f4f4; padding: 15px; border-radius: 5px;">
GET /health       - Health check
GET /diagnostics  - System diagnostics
POST /shutdown    - Shutdown browser instance
            </pre>
            
            <h2>Response Format:</h2>
            <pre style="background: #f4f4f4; padding: 15px; border-radius: 5px;">
{
    "success": true,
    "initial_url": "https://www.facebook.com/zuck",
    "final_url": "https://www.facebook.com/photo/?fbid=...",
    "page_title": "Facebook",
    "username": "zuck"  // For GET endpoints
}
            </pre>
            
            <h2>Quick Test Links:</h2>
            <ul>
                <li><a href="/health">Health Check</a></li>
                <li><a href="/diagnostics">System Diagnostics</a></li>
                <li><a href="/api/visit/zuck">Visit Zuck</a></li>
                <li><a href="/api/visit/marketplace">Visit Marketplace</a></li>
            </ul>
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
        fallback = None
        if WEBDRIVER_MANAGER_AVAILABLE:
            fallback = 'webdriver-manager available (will attempt download on demand)'
        diagnostics_info['chromedriver_check'] = {
            'status': 'not_found',
            'error': 'ChromeDriver not found or not working',
            'fallback': fallback
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
        else:
            if WEBDRIVER_MANAGER_AVAILABLE:
                try:
                    driver_path = download_with_webdriver_manager()
                    if driver_path:
                        service = Service(executable_path=driver_path)
                        test_driver = webdriver.Chrome(service=service, options=chrome_options)
                        test_driver.quit()
                        test_driver_result['status'] = 'success (downloaded via webdriver-manager)'
                    else:
                        raise RuntimeError('webdriver-manager did not return a driver path')
                except Exception as e:
                    test_driver_result['status'] = 'failed'
                    test_driver_result['error'] = str(e)
                    test_driver_result['traceback'] = traceback.format_exc()
            else:
                # Let Selenium Manager try
                try:
                    test_driver = webdriver.Chrome(options=chrome_options)
                    test_driver.quit()
                    test_driver_result['status'] = 'success (selenium-manager)'
                except Exception as e:
                    test_driver_result['status'] = 'failed'
                    test_driver_result['error'] = str(e)
                    test_driver_result['traceback'] = traceback.format_exc()
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
        # Optional per-request headed override
        headed_override = data.get('headed') if isinstance(data, dict) else None
        is_headless = None
        if headed_override is not None:
            try:
                # Accept booleans or truthy strings
                if isinstance(headed_override, bool):
                    is_headless = not headed_override
                else:
                    headed_str = str(headed_override).strip().lower()
                    headed_bool = headed_str in ("1", "true", "yes", "y")
                    is_headless = not headed_bool
            except Exception:
                pass
        
        result, error = navigate_and_interact(url, is_headless=is_headless)
        
        if error:
            return jsonify({'error': error}), 500
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/visit/<username>', methods=['GET'])
def visit_user(username):
    """Visit a Facebook user/page - GET endpoint for simple testing"""
    try:
        print(f"\n[API] GET /api/visit/{username}")
        
        # Handle special cases
        if username.lower() == 'marketplace':
            url = 'facebook.com/marketplace'
        else:
            url = username  # Will be processed by navigate_and_interact
        
        # Optional per-request headed override via query param: ?headed=true
        headed_param = request.args.get('headed')
        is_headless = None
        if headed_param is not None:
            headed_str = headed_param.strip().lower()
            headed_bool = headed_str in ("1", "true", "yes", "y")
            is_headless = not headed_bool
        
        result, error = navigate_and_interact(url, request_id=username[:8], is_headless=is_headless)
        
        if error:
            return jsonify({
                'success': False,
                'error': error,
                'username': username
            }), 500
        
        # Add username to result
        result['username'] = username
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'username': username
        }), 500

@app.route('/visit/<username>', methods=['GET'])
def visit_user_simple(username):
    """Simpler visit endpoint - just /visit/{username}"""
    return visit_user(username)

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
