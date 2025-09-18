#!/usr/bin/env python3
"""
Final Test - Verify WhatsApp Web Integration
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


def final_test():
    """Final test of WhatsApp Web integration"""
    print("🎯 Final WhatsApp Web Integration Test")
    print("=" * 50)
    
    service = WhatsAppWebService()
    
    # Test single message
    print("📱 Testing single message...")
    result = service.send_message(
        "+212643992808", 
        "🎉 SUCCESS! Your sc.py methods are now fully integrated into the web platform! This message was sent using your WhatsApp Web automation. ✅"
    )
    
    print(f"Result: {result}")
    
    if result['success']:
        print("✅ Single message: SUCCESS")
    else:
        print(f"❌ Single message failed: {result['error']}")
        return False
    
    # Test bulk messages
    print("\n📨 Testing bulk messages...")
    recipients = ["+212643992808", "+212713547536"]
    bulk_result = service.send_bulk_messages(
        recipients,
        "🚀 Bulk message test! Your sc.py WhatsApp automation is now powering a professional campaign system! 📊"
    )
    
    successful = sum(1 for r in bulk_result if r['success'])
    total = len(bulk_result)
    
    print(f"Bulk results: {successful}/{total} successful")
    
    for result in bulk_result:
        status = "✅" if result['success'] else "❌"
        print(f"  {status} {result['recipient']}")
        if not result['success']:
            print(f"    Error: {result['error']}")
    
    if successful > 0:
        print("✅ Bulk messaging: SUCCESS")
        return True
    else:
        print("❌ Bulk messaging: FAILED")
        return False


def main():
    try:
        success = final_test()
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 INTEGRATION COMPLETE!")
            print("✅ WhatsApp Web session active")
            print("✅ Single message sending works")
            print("✅ Bulk message sending works")
            print("✅ Your sc.py methods are fully integrated!")
            print("\n🚀 Next steps:")
            print("1. Open your web interface at http://localhost:3000")
            print("2. Try sending messages through the UI")
            print("3. Your messages will be sent FREE via WhatsApp Web!")
            print("4. Create campaigns with unlimited recipients!")
        else:
            print("❌ Integration needs attention")
            print("Check the error messages above")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")


if __name__ == "__main__":
    main()
