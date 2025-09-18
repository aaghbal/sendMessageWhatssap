#!/usr/bin/env python3
"""
Simple WhatsApp Web test using the Django management command approach
Run this from the Django project directory: whatsapp-automation/backend/
"""

import subprocess
import sys
import os


def run_django_command(command_args):
    """Run a Django management command"""
    try:
        result = subprocess.run(
            ['python', 'manage.py'] + command_args,
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        if result.stderr:
            print("Stderr:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        print("Stdout:", e.stdout)
        print("Stderr:", e.stderr)
        return False


def main():
    print("WhatsApp Web Integration Test")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists('manage.py'):
        print("Error: Please run this script from the Django project directory:")
        print("cd whatsapp-automation/backend/")
        print("python ../../test_whatsapp_simple.py")
        return
    
    print("1. Setting up WhatsApp Web session...")
    print("   This will open a browser window for QR code scanning.")
    
    if run_django_command(['setup_whatsapp']):
        print("✓ WhatsApp Web session setup completed!")
        
        print("\n2. You can now test sending messages through:")
        print("   - The web interface at http://localhost:8000")
        print("   - The API endpoint: POST /api/whatsapp/send-bulk/")
        print("   - Or using the Django shell:")
        print("     python manage.py shell")
        print("     >>> from whatsapp_messages.whatsapp_web_service import WhatsAppWebService")
        print("     >>> service = WhatsAppWebService()")
        print("     >>> service.send_message('+1234567890', 'Test message')")
        
    else:
        print("✗ WhatsApp Web session setup failed!")


if __name__ == "__main__":
    main()
