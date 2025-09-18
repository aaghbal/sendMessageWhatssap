#!/usr/bin/env python3
"""
Standalone WhatsApp Web Test Script
Based on the improved methods from sc.py integrated into the Django project

Usage:
1. Setup WhatsApp session: python test_whatsapp_web.py --setup
2. Send test messages: python test_whatsapp_web.py --send
3. Both setup and send: python test_whatsapp_web.py --setup --send
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


def setup_whatsapp_session():
    """Setup WhatsApp Web session with QR code scanning"""
    print("Setting up WhatsApp Web session...")
    service = WhatsAppWebService()
    return service.setup_session()


def test_send_messages():
    """Test sending messages using WhatsApp Web"""
    service = WhatsAppWebService()
    
    # Test phone numbers - replace with real numbers
    phone_numbers = [
        "+212713547536",  # Replace with real numbers
        "+212643992808",  # Replace with real numbers
    ]
    
    message = "Hello! This is a test message from the improved WhatsApp Web automation."
    
    print(f"\nSending test messages to {len(phone_numbers)} recipients...")
    
    # Test single message
    print("\n--- Testing Single Message ---")
    result = service.send_message(phone_numbers[0], message)
    print(f"Single message result: {result}")
    
    # Test bulk messages
    print("\n--- Testing Bulk Messages ---")
    results = service.send_bulk_messages(phone_numbers, message)
    
    print(f"\nBulk message results:")
    successful = 0
    for result in results:
        status = "✓ SUCCESS" if result['success'] else "✗ FAILED"
        print(f"  {result['recipient']}: {status}")
        if result['error']:
            print(f"    Error: {result['error']}")
        if result['success']:
            successful += 1
    
    print(f"\nSummary: {successful}/{len(results)} messages sent successfully")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='WhatsApp Web Test Script')
    parser.add_argument('--setup', action='store_true', help='Setup WhatsApp Web session')
    parser.add_argument('--send', action='store_true', help='Send test messages')
    
    args = parser.parse_args()
    
    if not args.setup and not args.send:
        print("Please specify --setup and/or --send")
        parser.print_help()
        return
    
    if args.setup:
        print("=== WhatsApp Web Session Setup ===")
        if setup_whatsapp_session():
            print("✓ Setup completed successfully!")
        else:
            print("✗ Setup failed!")
            if not args.send:
                return
    
    if args.send:
        print("\n=== Testing Message Sending ===")
        try:
            test_send_messages()
        except Exception as e:
            print(f"✗ Test failed: {str(e)}")
            print("Make sure to run --setup first to scan the QR code.")


if __name__ == "__main__":
    main()
