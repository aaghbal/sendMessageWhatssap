"""
Django management command to run campaigns using WhatsApp Web
Based on your sc.py methods
"""

from django.core.management.base import BaseCommand
from campaigns.models import Campaign
from campaigns.services import CampaignExecutionService


class Command(BaseCommand):
    help = 'Execute a campaign using WhatsApp Web automation (free messaging)'

    def add_arguments(self, parser):
        parser.add_argument(
            'campaign_id',
            type=int,
            help='ID of the campaign to execute'
        )
        parser.add_argument(
            '--service',
            choices=['whatsapp-web', 'twilio'],
            default='whatsapp-web',
            help='Service to use for sending messages (default: whatsapp-web)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually sending messages'
        )

    def handle(self, *args, **options):
        campaign_id = options['campaign_id']
        service_type = options['service']
        dry_run = options['dry_run']
        
        self.stdout.write(f'Processing campaign ID: {campaign_id}')
        
        try:
            campaign = Campaign.objects.get(id=campaign_id)
        except Campaign.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Campaign with ID {campaign_id} not found')
            )
            return
        
        # Show campaign details
        self.stdout.write(f'Campaign: {campaign.name}')
        self.stdout.write(f'Description: {campaign.description or "No description"}')
        self.stdout.write(f'Status: {campaign.status}')
        self.stdout.write(f'Recipients: {campaign.get_total_recipients()}')
        self.stdout.write(f'Message: {campaign.message_template.content[:100]}...')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No messages will be sent')
            )
            
            # Show recipients
            execution_service = CampaignExecutionService()
            recipients = execution_service._get_campaign_recipients(campaign)
            
            self.stdout.write(f'\nRecipients ({len(recipients)}):')
            for recipient in recipients[:10]:  # Show first 10
                self.stdout.write(f'  - {recipient["phone"]} ({recipient["name"] or "No name"})')
            
            if len(recipients) > 10:
                self.stdout.write(f'  ... and {len(recipients) - 10} more recipients')
            
            return
        
        # Confirm execution
        if campaign.status not in ['draft', 'scheduled']:
            self.stdout.write(
                self.style.ERROR(
                    f'Campaign is in {campaign.status} state and cannot be executed'
                )
            )
            return
        
        confirm = input(f'Execute campaign "{campaign.name}" with {service_type}? (y/N): ')
        if confirm.lower() != 'y':
            self.stdout.write('Campaign execution cancelled')
            return
        
        # Execute campaign
        self.stdout.write(f'Starting campaign execution with {service_type}...')
        
        execution_service = CampaignExecutionService()
        use_whatsapp_web = (service_type == 'whatsapp-web')
        
        result = execution_service.execute_campaign(campaign_id, use_whatsapp_web)
        
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS('Campaign executed successfully!')
            )
            self.stdout.write(f"Service used: {result['service_used']}")
            self.stdout.write(f"Total recipients: {result['total_recipients']}")
            
            results = result['results']
            self.stdout.write(f"Successful sends: {results['successful_sends']}")
            self.stdout.write(f"Failed sends: {results['failed_sends']}")
            self.stdout.write(f"Cost: ${results.get('cost', 0):.2f}")
            
            if results['failed_sends'] > 0:
                self.stdout.write(
                    self.style.WARNING(
                        f'{results["failed_sends"]} messages failed to send'
                    )
                )
        else:
            self.stdout.write(
                self.style.ERROR(f'Campaign execution failed: {result["error"]}')
            )
            
            if 'WhatsApp Web session' in result["error"]:
                self.stdout.write(
                    self.style.WARNING(
                        'Try running: python manage.py setup_whatsapp'
                    )
                )
    
    def show_campaign_recipients(self, campaign):
        """Helper method to show campaign recipients"""
        recipients = []
        
        # Add individual phone numbers
        for phone in campaign.target_phones.all():
            recipients.append({
                'phone': phone.phone_number,
                'name': phone.contact_name or 'No name',
                'source': 'individual'
            })
        
        # Add phone numbers from groups
        for group in campaign.target_groups.all():
            for phone in group.phone_numbers.all():
                if not any(r['phone'] == phone.phone_number for r in recipients):
                    recipients.append({
                        'phone': phone.phone_number,
                        'name': phone.contact_name or 'No name',
                        'source': f'group: {group.name}'
                    })
        
        return recipients
