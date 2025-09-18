#!/usr/bin/env python3
"""
Script to expire WhatsApp Web session for testing auto-recreation functionality
This will clear the current session so we can test the QR code popup in campaigns
"""

import os
import sys
import django
from pathlib import Path
import shutil

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_automation.settings')
django.setup()

from whatsapp_messages.whatsapp_web_service import WhatsAppWebService
from django.conf import settings
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def expire_whatsapp_session():
    """Expire the current WhatsApp Web session for testing"""
    
    print("🧪 Expiring WhatsApp Web Session for Testing")
    print("=" * 50)
    
    service = WhatsAppWebService()
    session_dir = service.session_dir
    backup_dir = os.path.join(settings.BASE_DIR, 'whatsapp_session_backup')
    
    print(f"📁 Session directory: {session_dir}")
    print(f"💾 Backup directory: {backup_dir}")
    
    # Clear current session
    if os.path.exists(session_dir):
        try:
            shutil.rmtree(session_dir)
            print("✅ Current WhatsApp Web session expired (deleted)")
        except Exception as e:
            print(f"❌ Failed to expire session: {e}")
            return False
    else:
        print("ℹ️  No current session found")
    
    # Also clear backup to force QR code scanning
    if os.path.exists(backup_dir):
        try:
            shutil.rmtree(backup_dir)
            print("✅ Session backup also cleared (to force QR code)")
        except Exception as e:
            print(f"⚠️  Failed to clear backup: {e}")
    else:
        print("ℹ️  No backup found")
    
    print("\n" + "=" * 50)
    print("🎯 Session Successfully Expired!")
    print("=" * 50)
    print("📋 Now you can test the auto QR code functionality:")
    print("1. Go to your campaign in the web interface")
    print("2. Click 'Send Messages' button")
    print("3. Chrome should automatically open with QR code")
    print("4. Scan the QR code within 60 seconds")
    print("5. Campaign will continue automatically!")
    print("\n💡 Expected behavior:")
    print("- Chrome window opens with WhatsApp Web QR code")
    print("- Clear instructions displayed in terminal")
    print("- 60-second timeout for scanning")
    print("- Campaign continues after successful scan")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    expire_whatsapp_session()
