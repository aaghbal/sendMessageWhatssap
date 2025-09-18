"""
WhatsApp Web Automation Script

Usage:
1. First time setup (requires QR code scan):
   python3 sc.py --setup

2. Send messages (headless mode):
   python3 sc.py

The script will automatically detect if setup is needed.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import os
import urllib.parse

def setup_whatsapp_session():
    """Setup WhatsApp Web session with QR code scanning"""
    print("Setting up WhatsApp Web session...")
    
    options = webdriver.ChromeOptions()
    options.add_argument('user-data-dir=./whatsapp_session')
    
    # Install ChromeDriver automatically
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    driver.get('https://web.whatsapp.com')
    
    print("\n" + "="*50)
    print("IMPORTANT: Scan the QR code in the browser window")
    print("="*50 + "\n")
    
    # Wait for user to scan QR code
    try:
        # Wait for side panel to load (indicates successful login)
        WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.ID, "side"))
        )
        print("✓ WhatsApp Web logged in successfully!")
        time.sleep(5)
        driver.quit()
        return True
    except:
        print("✗ Failed to login to WhatsApp Web")
        driver.quit()
        return False

def send_whatsapp_messages(phone_numbers, message):
    """Send messages after session is established"""
    options = webdriver.ChromeOptions()
    options.add_argument('user-data-dir=./whatsapp_session')
    
    # Enable headless mode for automated sending
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-web-security')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(ChromeDriverManager().install())
    
    try:
        driver = webdriver.Chrome(service=service, options=options)
        
        # Add script to avoid detection
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # First, check if we're still logged in
        driver.get('https://web.whatsapp.com')
        time.sleep(10)
        
        # Check if we need to login again
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "side"))
            )
            print("✓ WhatsApp Web session is active")
        except:
            print("✗ WhatsApp session expired. Please run setup again.")
            driver.quit()
            return
    
        for phone in phone_numbers:
            try:
                # Clean phone number
                phone_clean = phone.replace('+', '').replace(' ', '').replace('-', '')
                
                print(f"Sending message to {phone}...")
                
                # Open chat with encoded message
                encoded_message = urllib.parse.quote(message)
                driver.get(f'https://web.whatsapp.com/send?phone={phone_clean}&text={encoded_message}')
                
                # Wait for the page to load
                time.sleep(15)
                
                # Wait and click send button - try multiple selectors
                try:
                    # Try different selectors for the send button
                    send_button = WebDriverWait(driver, 30).until(
                        EC.any_of(
                            EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Send"]')),
                            EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]')),
                            EC.element_to_be_clickable((By.XPATH, '//button[contains(@class, "send")]')),
                            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="send"]')),
                            EC.element_to_be_clickable((By.XPATH, '//div[@role="button"][@data-tab="11"]'))
                        )
                    )
                    send_button.click()
                    
                    print(f"✓ Message sent to {phone}")
                    time.sleep(8)
                    
                except Exception as send_error:
                    print(f"✗ Could not find send button for {phone}: {str(send_error)}")
                
            except Exception as e:
                print(f"✗ Failed to send to {phone}: {str(e)}")
                # Continue with next number instead of crashing
        
    except Exception as e:
        print(f"✗ Failed to initialize driver: {str(e)}")
    finally:
        try:
            driver.quit()
        except:
            pass  # Ignore errors when closing driver

# Main execution
if __name__ == "__main__":
    import sys
    
    # Check for setup flag
    force_setup = '--setup' in sys.argv
    
    # Check if session exists or if setup is forced
    if not os.path.exists('./whatsapp_session/Default') or force_setup:
        print("Setting up WhatsApp session...")
        if not setup_whatsapp_session():
            print("Setup failed. Exiting.")
            exit(1)
        print("Setup completed! You can now run the script without --setup flag.")
        if force_setup:
            exit(0)  # Exit after setup if explicitly requested
    
    # Now send messages
    phone_numbers = [
        "+212713547536",  # Replace with real numbers
        "+212643992808",  # Replace with real numbers
    ]
    
    message = "Hello! This is an automated message from Python."
    
    print("\nSending messages in headless mode...")
    send_whatsapp_messages(phone_numbers, message)
    print("\nDone!")
# phone_numbers = [
#     "+212643992808",  # Include country code
#     "+212698200321",
#     "+212713547536"  # Add more numbers as needed
# ]