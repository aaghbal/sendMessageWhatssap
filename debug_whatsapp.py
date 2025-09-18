#!/usr/bin/env python3
"""
WhatsApp Web Debug Script
Test and debug WhatsApp Web session issues
"""

import os
import sys
import django
from pathlib import Path

# Add the Django project to Python path
project_root = Path(__file__).parent / 'whatsapp-automation' / 'backend'
sys.path.insert(0, str(project_root))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_automation.settings')
django.setup()

from whatsapp_messages.whatsapp_web_service import WhatsAppWebService
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time


def debug_whatsapp_session():
    """Debug WhatsApp Web session"""
    print("🔍 Debugging WhatsApp Web session...")
    
    service = WhatsAppWebService()
    session_dir = service.session_dir
    
    print(f"📁 Session directory: {session_dir}")
    
    # Check if session exists
    default_path = os.path.join(session_dir, 'Default')
    if os.path.exists(default_path):
        print("✅ Session folder exists")
    else:
        print("❌ Session folder missing - need to run setup")
        return False
    
    # Test WhatsApp Web connection
    print("🌐 Testing WhatsApp Web connection...")
    
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-data-dir={session_dir}')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # Remove headless for debugging
    # options.add_argument('--headless')
    
    service_obj = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service_obj, options=options)
    
    try:
        print("🔗 Opening WhatsApp Web...")
        driver.get('https://web.whatsapp.com')
        
        # Wait a bit for page to load
        time.sleep(5)
        
        # Check current page state
        print("📊 Checking page state...")
        
        # Check for QR code
        try:
            qr_code = driver.find_element(By.CSS_SELECTOR, "[data-testid='qr-code']")
            if qr_code:
                print("📱 QR code found - session not logged in!")
                print("💡 You need to scan the QR code to login")
                print("🔧 Run: python manage.py setup_whatsapp")
                return False
        except:
            print("✅ No QR code found")
        
        # Check for side panel (logged in indicator)
        try:
            side_panel = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "side"))
            )
            if side_panel:
                print("✅ WhatsApp Web is logged in!")
                
                # Get some basic info
                try:
                    # Check for user info
                    user_info = driver.find_element(By.CSS_SELECTOR, '[data-testid="avatar-image"]')
                    if user_info:
                        print("👤 User avatar found - fully logged in")
                except:
                    print("⚠️  Avatar not found but side panel exists")
                
                return True
        except:
            print("❌ Side panel not found - not logged in")
            return False
    
    except Exception as e:
        print(f"❌ Error testing session: {str(e)}")
        return False
    
    finally:
        driver.quit()


def test_message_sending():
    """Test sending a message"""
    print("\n📨 Testing message sending...")
    
    service = WhatsAppWebService()
    
    # Test with the phone number from your screenshot
    test_phone = "+212643992808"
    test_message = "Test message from debug script"
    
    print(f"📞 Sending to: {test_phone}")
    print(f"💬 Message: {test_message}")
    
    result = service.send_message(test_phone, test_message)
    
    print(f"📊 Result: {result}")
    
    if result['success']:
        print("✅ Message sent successfully!")
    else:
        print(f"❌ Message failed: {result['error']}")
        
        # Provide specific troubleshooting
        if "session not active" in result['error'].lower():
            print("💡 Solution: Run 'python manage.py setup_whatsapp' to scan QR code")
        elif "invalid phone number" in result['error'].lower():
            print("💡 Solution: Check phone number format (include country code like +212...)")
        elif "send button" in result['error'].lower():
            print("💡 Solution: WhatsApp Web interface might have changed - check for updates")
    
    return result['success']


def main():
    print("🛠️  WhatsApp Web Debug Tool")
    print("=" * 50)
    
    # Step 1: Check session
    session_ok = debug_whatsapp_session()
    
    if not session_ok:
        print("\n🚨 Session issue detected!")
        print("🔧 Run this command to fix:")
        print("   python manage.py setup_whatsapp")
        return
    
    # Step 2: Test message sending
    message_ok = test_message_sending()
    
    if message_ok:
        print("\n🎉 Everything is working!")
        print("✅ WhatsApp Web session is active")
        print("✅ Message sending is functional")
        print("🚀 Your web interface should work now!")
    else:
        print("\n🔍 Debug info:")
        print("✅ Session is active")
        print("❌ Message sending failed")
        print("💡 Check the error details above")


if __name__ == "__main__":
    main()
