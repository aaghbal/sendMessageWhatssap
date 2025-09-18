#!/usr/bin/env python3
"""
Campaign Test Script - Using WhatsApp Web Methods from sc.py
Test your campaigns system with WhatsApp Web automation

Usage:
  python test_campaigns.py --setup          # Setup WhatsApp Web session
  python test_campaigns.py --create         # Create test campaign
  python test_campaigns.py --run <id>       # Run campaign by ID
  python test_campaigns.py --list           # List all campaigns
  python test_campaigns.py --status <id>    # Check campaign status
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

from campaigns.models import Campaign, CampaignMessage, CampaignAnalytics
from campaigns.services import CampaignExecutionService
from whatsapp_messages.models import MessageTemplate
from contacts.models import PhoneNumber, PhoneNumberGroup
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


def setup_whatsapp_web():
    """Setup WhatsApp Web session"""
    print("🔧 Setting up WhatsApp Web session...")
    
    from whatsapp_messages.whatsapp_web_service import WhatsAppWebService
    service = WhatsAppWebService()
    
    success = service.setup_session()
    
    if success:
        print("✅ WhatsApp Web session setup completed!")
        print("🎯 You can now run campaigns for FREE!")
        return True
    else:
        print("❌ WhatsApp Web session setup failed!")
        return False


def create_test_campaign():
    """Create a test campaign with sample data"""
    print("📝 Creating test campaign...")
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    if created:
        print("👤 Created test user")
    
    # Create or get message template
    template, created = MessageTemplate.objects.get_or_create(
        user=user,
        name='Test Campaign Template',
        defaults={
            'message_type': 'text',
            'content': '🚀 Hello! This is a test message from your WhatsApp campaign system powered by sc.py methods! 📱✨'
        }
    )
    if created:
        print("📄 Created test message template")
    
    # Create test phone numbers
    test_phones = [
        "+212713547536",  # From your sc.py
        "+212643992808",  # From your sc.py
    ]
    
    phone_objects = []
    for phone in test_phones:
        phone_obj, created = PhoneNumber.objects.get_or_create(
            user=user,
            phone_number=phone,
            defaults={'contact_name': f'Test Contact {phone[-4:]}'}
        )
        phone_objects.append(phone_obj)
        if created:
            print(f"📞 Created test phone number: {phone}")
    
    # Create test group
    group, created = PhoneNumberGroup.objects.get_or_create(
        user=user,
        name='Test Campaign Group',
        defaults={'description': 'Test group for campaign testing'}
    )
    if created:
        print("👥 Created test phone group")
        group.phone_numbers.set(phone_objects)
    
    # Create campaign
    campaign = Campaign.objects.create(
        user=user,
        name=f'Test WhatsApp Web Campaign {timezone.now().strftime("%Y-%m-%d %H:%M")}',
        description='Test campaign using WhatsApp Web automation from sc.py',
        message_template=template,
        status='draft'
    )
    
    # Add recipients
    campaign.target_phones.set(phone_objects)
    campaign.target_groups.add(group)
    
    print(f"🎯 Created campaign: {campaign.name}")
    print(f"   ID: {campaign.id}")
    print(f"   Recipients: {campaign.get_total_recipients()}")
    print(f"   Message: {template.content}")
    
    return campaign


def list_campaigns():
    """List all campaigns"""
    print("📋 Listing all campaigns...")
    
    campaigns = Campaign.objects.all().order_by('-created_at')
    
    if not campaigns:
        print("   No campaigns found. Create one with --create")
        return
    
    for campaign in campaigns:
        status_emoji = {
            'draft': '📝',
            'scheduled': '⏰',
            'running': '🏃',
            'completed': '✅',
            'failed': '❌',
            'cancelled': '🚫'
        }.get(campaign.status, '❓')
        
        print(f"   {status_emoji} ID: {campaign.id} | {campaign.name}")
        print(f"      Status: {campaign.status} | Recipients: {campaign.get_total_recipients()}")
        print(f"      Created: {campaign.created_at.strftime('%Y-%m-%d %H:%M')}")
        if campaign.status in ['completed', 'failed']:
            print(f"      Sent: {campaign.get_sent_count()} | Failed: {campaign.get_failed_count()}")
        print()


def run_campaign(campaign_id):
    """Run a campaign using WhatsApp Web"""
    print(f"🚀 Running campaign ID: {campaign_id}")
    
    try:
        campaign = Campaign.objects.get(id=campaign_id)
    except Campaign.DoesNotExist:
        print(f"❌ Campaign with ID {campaign_id} not found")
        return
    
    print(f"📝 Campaign: {campaign.name}")
    print(f"📊 Status: {campaign.status}")
    print(f"👥 Recipients: {campaign.get_total_recipients()}")
    print(f"💬 Message: {campaign.message_template.content[:100]}...")
    
    if campaign.status not in ['draft', 'scheduled']:
        print(f"❌ Campaign is in '{campaign.status}' state and cannot be executed")
        return
    
    # Confirm execution
    response = input("🤔 Execute this campaign using WhatsApp Web? (y/N): ")
    if response.lower() != 'y':
        print("🚫 Campaign execution cancelled")
        return
    
    # Execute campaign
    print("⚡ Starting campaign execution with WhatsApp Web...")
    
    execution_service = CampaignExecutionService()
    result = execution_service.execute_campaign(campaign_id, use_whatsapp_web=True)
    
    if result['success']:
        print("🎉 Campaign executed successfully!")
        print(f"   Service: {result['service_used']}")
        print(f"   Total recipients: {result['total_recipients']}")
        
        results = result['results']
        print(f"   ✅ Successful: {results['successful_sends']}")
        print(f"   ❌ Failed: {results['failed_sends']}")
        print(f"   💰 Cost: ${results.get('cost', 0):.2f} (FREE with WhatsApp Web!)")
        
        if results['failed_sends'] > 0:
            print(f"   ⚠️  {results['failed_sends']} messages failed")
    else:
        print(f"❌ Campaign execution failed: {result['error']}")
        
        if 'WhatsApp Web session' in result['error']:
            print("💡 Try running: python test_campaigns.py --setup")


def check_campaign_status(campaign_id):
    """Check campaign status and analytics"""
    print(f"📊 Checking status for campaign ID: {campaign_id}")
    
    execution_service = CampaignExecutionService()
    status_result = execution_service.get_campaign_status(campaign_id)
    
    if status_result['success']:
        print(f"📝 Campaign: {status_result['campaign_name']}")
        print(f"📊 Status: {status_result['status']}")
        print(f"👥 Total recipients: {status_result['total_recipients']}")
        print(f"✅ Messages sent: {status_result['messages_sent']}")
        print(f"❌ Messages failed: {status_result['messages_failed']}")
        
        if status_result['started_at']:
            print(f"🕐 Started: {status_result['started_at']}")
        if status_result['completed_at']:
            print(f"🏁 Completed: {status_result['completed_at']}")
        
        analytics = status_result.get('analytics')
        if analytics:
            print(f"📈 Delivery rate: {analytics['delivery_rate']:.1f}%")
            print(f"👀 Read rate: {analytics['read_rate']:.1f}%")
            print(f"💰 Cost estimate: ${analytics['cost_estimate']:.2f}")
    else:
        print(f"❌ {status_result['error']}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='WhatsApp Campaign Test Script')
    parser.add_argument('--setup', action='store_true', help='Setup WhatsApp Web session')
    parser.add_argument('--create', action='store_true', help='Create test campaign')
    parser.add_argument('--run', type=int, metavar='ID', help='Run campaign by ID')
    parser.add_argument('--list', action='store_true', help='List all campaigns')
    parser.add_argument('--status', type=int, metavar='ID', help='Check campaign status')
    
    args = parser.parse_args()
    
    if not any([args.setup, args.create, args.run, args.list, args.status]):
        print("WhatsApp Campaign System - Powered by sc.py methods! 🚀")
        print()
        parser.print_help()
        return
    
    print("🎯 WhatsApp Campaign System - Using sc.py Methods")
    print("=" * 50)
    
    if args.setup:
        setup_whatsapp_web()
    
    if args.create:
        create_test_campaign()
    
    if args.list:
        list_campaigns()
    
    if args.run:
        run_campaign(args.run)
    
    if args.status:
        check_campaign_status(args.status)
    
    print("\n✨ Done! Your campaigns are powered by the sc.py WhatsApp Web methods!")


if __name__ == "__main__":
    main()
