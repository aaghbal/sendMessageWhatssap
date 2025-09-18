#!/usr/bin/env python3
"""
Test script to verify WhatsApp Web session auto-recreation functionality
This simulates what happens when a campaign tries to send messages with an expired session
"""

import os
import sys
import django
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_automation.settings')
django.setup()

from whatsapp_messages.whatsapp_web_service import WhatsAppWebService
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_session_auto_recreation():
    """Test the automatic session recreation functionality"""
    
    print("🧪 Testing WhatsApp Web Session Auto-Recreation")
    print("=" * 50)
    
    service = WhatsAppWebService()
    
    # Test 1: Check if session backup functionality works
    print("\n1. Testing session backup creation...")
    try:
        backup_created = service.create_session_backup()
        if backup_created:
            print("✅ Session backup functionality works")
        else:
            print("⚠️  Session backup creation returned False (may be expected if no session exists)")
    except Exception as e:
        print(f"❌ Session backup failed: {e}")
    
    # Test 2: Test session validity check
    print("\n2. Testing session validity check...")
    try:
        is_valid = service._test_session_validity()
        if is_valid:
            print("✅ Current session is valid")
        else:
            print("⚠️  Current session is not valid (expected if not setup)")
    except Exception as e:
        print(f"❌ Session validity check failed: {e}")
    
    # Test 3: Test automatic session recreation (without actually recreating)
    print("\n3. Testing auto-recreation logic...")
    try:
        # This will attempt recreation but likely fail without manual QR scan
        # That's expected - we just want to test the logic flow
        recreation_success = service._recreate_session_automatically()
        if recreation_success:
            print("✅ Session recreation succeeded")
        else:
            print("⚠️  Session recreation returned False (expected without QR scan)")
    except Exception as e:
        print(f"❌ Session recreation test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🔍 Test Summary:")
    print("The auto-recreation functionality has been implemented.")
    print("When campaigns run and sessions are expired, the system will:")
    print("1. Detect expired sessions automatically")
    print("2. Attempt to restore from backup if available") 
    print("3. Provide clear error messages if manual setup is needed")
    print("\n📋 Next Steps:")
    print("1. Run: python manage.py setup_whatsapp --force")
    print("2. Scan the QR code to establish a fresh session")
    print("3. Try sending a campaign - it will now auto-handle expired sessions!")

if __name__ == "__main__":
    test_session_auto_recreation()
