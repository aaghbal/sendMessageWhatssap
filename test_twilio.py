#!/usr/bin/env python3
"""
Test script to verify Twilio WhatsApp integration
"""

import os
import sys
from pathlib import Path

# Add the Django project to Python path
django_project_path = Path(__file__).parent / "whatsapp-automation" / "backend"
sys.path.append(str(django_project_path))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_automation.settings')
import django
django.setup()

from whatsapp_messages.services import TwilioWhatsAppService

def test_twilio_connection():
    """Test if Twilio credentials are working"""
    print("Testing Twilio WhatsApp integration...")
    
    try:
        service = TwilioWhatsAppService()
        print(f"✓ Twilio service initialized")
        print(f"✓ Account SID: {service.client.username}")
        print(f"✓ From Phone: {service.from_phone}")
        
        # Test sending a message to your phone
        test_phone = "+212726982582"  # Your phone from sc.py
        test_message = "🎉 Test message from your WhatsApp automation system!"
        
        print(f"\nSending test message to {test_phone}...")
        result = service.send_message(test_phone, test_message)
        
        if result['success']:
            print(f"✅ Message sent successfully!")
            print(f"   Message SID: {result['message_sid']}")
            print(f"   Status: {result['status']}")
            print(f"\n🔔 Check your WhatsApp on {test_phone} for the message!")
        else:
            print(f"❌ Failed to send message:")
            print(f"   Error: {result['error']}")
            
    except Exception as e:
        print(f"❌ Error initializing Twilio service: {e}")
        print("\n💡 Make sure you have:")
        print("   1. Added your real Auth Token to backend/.env")
        print("   2. Joined the Twilio WhatsApp sandbox")
        print("   3. Restarted the backend server")

if __name__ == "__main__":
    test_twilio_connection()
