#!/usr/bin/env python3
"""
Facebook Headless Browser Navigator
This script launches a headless Chrome browser optimized for Facebook navigation.
It performs automated key sequences after navigating to any Facebook URL.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time


def launch_headless_browser():
    """
    Launch a lightweight headless Chrome browser optimized for Facebook.
    """
    # Configure Chrome options for headless mode
    chrome_options = Options()
    
    # Enable headless mode
    chrome_options.add_argument("--headless")
    
    # Additional lightweight optimizations
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    chrome_options.add_argument("--disable-extensions")
    # Note: Keeping images enabled for Facebook functionality
    
    # Set window size
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Reduce memory usage
    chrome_options.add_argument("--memory-pressure-off")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    chrome_options.add_argument("--disable-features=TranslateUI")
    chrome_options.add_argument("--disable-ipc-flooding-protection")
    
    # User agent for Facebook compatibility
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    try:
        # Initialize the Chrome driver
        print("Launching headless browser for Facebook...")
        driver = webdriver.Chrome(options=chrome_options)
        
        print("Headless browser launched successfully!")
        return driver
        
    except Exception as e:
        print(f"Error launching headless browser: {e}")
        print("\nMake sure you have:")
        print("1. Chrome browser installed")
        print("2. ChromeDriver installed (or use webdriver-manager)")
        print("3. Selenium installed: pip install selenium")
        return None


def navigate_to_facebook_url(driver, url):
    """
    Navigate to a Facebook URL and perform the automated key sequence.
    
    Args:
        driver: Selenium WebDriver instance
        url: The Facebook URL to navigate to
    
    Returns:
        The final URL after all actions are performed
    """
    try:
        print(f"\nNavigating to: {url}")
        driver.get(url)
        
        # Wait 2 seconds after navigation
        print("Waiting 2 seconds...")
        time.sleep(2)
        
        # Create action chain for key presses
        actions = ActionChains(driver)
        
        # Press Escape key once
        print("Pressing Escape key...")
        actions.send_keys(Keys.ESCAPE).perform()
        time.sleep(0.5)  # Small delay between actions
        
        # Press Tab 7 times
        print("Pressing Tab 7 times...")
        for i in range(7):
            actions.send_keys(Keys.TAB).perform()
            time.sleep(0.2)  # Small delay between tabs
        
        # Press Enter
        print("Pressing Enter...")
        actions.send_keys(Keys.ENTER).perform()
        
        # Wait a moment for any page changes
        time.sleep(2)
        
        # Get the current URL (live URL after all actions)
        current_url = driver.current_url
        print(f"\nLive URL: {current_url}")
        print(f"Page Title: {driver.title}")
        
        return current_url
        
    except Exception as e:
        print(f"Error during navigation: {e}")
        return None


def main():
    """
    Main function for Facebook navigation with automated actions.
    """
    driver = launch_headless_browser()
    
    if driver:
        try:
            # Get URL from user
            print("\n" + "="*50)
            print("Facebook URL Navigator")
            print("="*50)
            
            while True:
                print("\nEnter a Facebook URL (or 'quit' to exit):")
                url = input("> ").strip()
                
                if url.lower() == 'quit':
                    break
                
                # Validate if it's a Facebook URL or add Facebook domain if needed
                if not url.startswith('http'):
                    if url.startswith('facebook.com') or url.startswith('www.facebook.com'):
                        url = 'https://' + url
                    else:
                        # Assume it's a Facebook path
                        url = 'https://www.facebook.com/' + url.lstrip('/')
                
                # Perform navigation and automated actions
                final_url = navigate_to_facebook_url(driver, url)
                
                if final_url:
                    print(f"\nSuccessfully navigated and performed actions!")
                    print(f"Final URL: {final_url}")
                else:
                    print("\nNavigation failed. Please try again.")
                
                # Ask if user wants to navigate to another URL
                print("\nPress Enter to navigate to another URL, or type 'quit' to exit")
                if input().lower() == 'quit':
                    break
            
        finally:
            # Always close the browser when done
            print("\nClosing browser...")
            driver.quit()
            print("Browser closed.")
    else:
        print("\nFailed to launch headless browser.")
        print("\nTo install required dependencies, run:")
        print("pip install selenium")
        print("\nFor automatic ChromeDriver management, you can also install:")
        print("pip install webdriver-manager")


if __name__ == "__main__":
    main()
