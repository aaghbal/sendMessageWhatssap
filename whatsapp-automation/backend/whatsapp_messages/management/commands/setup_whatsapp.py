"""
Django management command to setup WhatsApp Web session
Based on the setup method from sc.py
"""

from django.core.management.base import BaseCommand
from whatsapp_messages.whatsapp_web_service import WhatsAppWebService


class Command(BaseCommand):
    help = 'Setup WhatsApp Web session by scanning QR code'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force setup even if session already exists',
        )

    def handle(self, *args, **options):
        self.stdout.write('Setting up WhatsApp Web session...')
        
        service = WhatsAppWebService()
        
        # Check if session already exists
        import os
        session_path = os.path.join(service.session_dir, 'Default')
        
        if os.path.exists(session_path) and not options['force']:
            self.stdout.write(
                self.style.WARNING(
                    'WhatsApp Web session already exists. Use --force to recreate.'
                )
            )
            return
        
        success = service.setup_session()
        
        if success:
            self.stdout.write(
                self.style.SUCCESS(
                    'WhatsApp Web session setup completed successfully!'
                )
            )
            self.stdout.write(
                'You can now send messages through the web interface or API.'
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    'Failed to setup WhatsApp Web session. Please try again.'
                )
            )
