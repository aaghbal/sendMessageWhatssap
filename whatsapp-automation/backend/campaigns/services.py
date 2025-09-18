"""
Campaign Execution Service using WhatsApp Web
Integrates your sc.py methods with the campaigns system
"""

from django.utils import timezone
from django.db import transaction
from campaigns.models import Campaign, CampaignMessage, CampaignAnalytics
from whatsapp_messages.whatsapp_web_service import WhatsAppWebService
from whatsapp_messages.services import TwilioWhatsAppService
import logging
from typing import List, Dict, Any
import time

logger = logging.getLogger(__name__)


class CampaignExecutionService:
    """Service to execute campaigns using WhatsApp Web automation"""
    
    def __init__(self):
        self.whatsapp_web_service = WhatsAppWebService()
        self.twilio_service = TwilioWhatsAppService()
    
    def execute_campaign(self, campaign_id: int, use_whatsapp_web: bool = True) -> Dict[str, Any]:
        """
        Execute a campaign using WhatsApp Web or Twilio
        
        Args:
            campaign_id: ID of the campaign to execute
            use_whatsapp_web: Whether to use WhatsApp Web (free) or Twilio (paid)
            
        Returns:
            Dict with execution results
        """
        try:
            campaign = Campaign.objects.get(id=campaign_id)
            
            # Check if campaign is in valid state
            if campaign.status not in ['draft', 'scheduled']:
                return {
                    'success': False,
                    'error': f'Campaign is in {campaign.status} state and cannot be executed'
                }
            
            # Update campaign status
            campaign.status = 'running'
            campaign.started_at = timezone.now()
            campaign.save()
            
            logger.info(f"Starting campaign execution: {campaign.name}")
            
            # Get all recipients
            recipients = self._get_campaign_recipients(campaign)
            
            if not recipients:
                campaign.status = 'failed'
                campaign.completed_at = timezone.now()
                campaign.save()
                return {
                    'success': False,
                    'error': 'No recipients found for campaign'
                }
            
            # Create campaign messages
            self._create_campaign_messages(campaign, recipients)
            
            # Execute based on service choice
            if use_whatsapp_web:
                results = self._execute_with_whatsapp_web(campaign)
            else:
                results = self._execute_with_twilio(campaign)
            
            # Update campaign status
            campaign.status = 'completed'
            campaign.completed_at = timezone.now()
            campaign.save()
            
            # Update analytics
            self._update_campaign_analytics(campaign)
            
            logger.info(f"Campaign execution completed: {campaign.name}")
            
            return {
                'success': True,
                'campaign_id': campaign.id,
                'campaign_name': campaign.name,
                'total_recipients': len(recipients),
                'service_used': 'WhatsApp Web' if use_whatsapp_web else 'Twilio',
                'results': results
            }
            
        except Campaign.DoesNotExist:
            return {
                'success': False,
                'error': f'Campaign with ID {campaign_id} not found'
            }
        except Exception as e:
            logger.error(f"Campaign execution failed: {str(e)}")
            # Update campaign status to failed
            try:
                campaign = Campaign.objects.get(id=campaign_id)
                campaign.status = 'failed'
                campaign.completed_at = timezone.now()
                campaign.save()
            except:
                pass
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_campaign_recipients(self, campaign: Campaign) -> List[Dict[str, str]]:
        """Get all recipients for a campaign"""
        recipients = []
        
        # Add individual phone numbers
        for phone in campaign.target_phones.all():
            recipients.append({
                'phone': phone.phone_number,
                'name': phone.contact_name or '',
                'source': 'individual'
            })
        
        # Add phone numbers from groups
        for group in campaign.target_groups.all():
            for phone in group.phone_numbers.all():
                # Avoid duplicates
                if not any(r['phone'] == phone.phone_number for r in recipients):
                    recipients.append({
                        'phone': phone.phone_number,
                        'name': phone.contact_name or '',
                        'source': f'group_{group.name}'
                    })
        
        return recipients
    
    def _create_campaign_messages(self, campaign: Campaign, recipients: List[Dict[str, str]]):
        """Create CampaignMessage objects for tracking"""
        campaign_messages = []
        
        for recipient in recipients:
            campaign_message = CampaignMessage(
                campaign=campaign,
                recipient_phone=recipient['phone'],
                recipient_name=recipient['name'],
                message_content=campaign.message_template.content,
                status='pending'
            )
            campaign_messages.append(campaign_message)
        
        # Bulk create for efficiency
        CampaignMessage.objects.bulk_create(campaign_messages)
    
    def _execute_with_whatsapp_web(self, campaign: Campaign) -> Dict[str, Any]:
        """Execute campaign using WhatsApp Web service (your sc.py methods)"""
        logger.info(f"Executing campaign {campaign.name} with WhatsApp Web")
        
        # Get pending messages
        pending_messages = campaign.campaign_messages.filter(status='pending')
        
        # Prepare recipients list for bulk sending
        recipients = [msg.recipient_phone for msg in pending_messages]
        message_content = campaign.message_template.content
        
        # Use the improved bulk messaging from your sc.py
        results = self.whatsapp_web_service.send_bulk_messages(recipients, message_content)
        
        # Update campaign messages with results
        successful_sends = 0
        failed_sends = 0
        
        for result in results:
            try:
                campaign_message = pending_messages.get(recipient_phone=result['recipient'])
                
                if result['success']:
                    campaign_message.status = 'sent'
                    campaign_message.twilio_sid = result.get('message_sid')
                    campaign_message.sent_at = timezone.now()
                    successful_sends += 1
                else:
                    campaign_message.status = 'failed'
                    campaign_message.error_message = result.get('error')
                    failed_sends += 1
                
                campaign_message.save()
                
            except CampaignMessage.DoesNotExist:
                logger.warning(f"Campaign message not found for recipient: {result['recipient']}")
        
        return {
            'service': 'WhatsApp Web',
            'total_processed': len(results),
            'successful_sends': successful_sends,
            'failed_sends': failed_sends,
            'cost': 0.00,  # WhatsApp Web is free
            'details': results
        }
    
    def _execute_with_twilio(self, campaign: Campaign) -> Dict[str, Any]:
        """Execute campaign using Twilio service"""
        logger.info(f"Executing campaign {campaign.name} with Twilio")
        
        # Get pending messages
        pending_messages = campaign.campaign_messages.filter(status='pending')
        
        # Prepare recipients list
        recipients = [msg.recipient_phone for msg in pending_messages]
        message_content = campaign.message_template.content
        
        # Use Twilio bulk messaging
        results = self.twilio_service.send_bulk_messages(recipients, message_content)
        
        # Update campaign messages with results
        successful_sends = 0
        failed_sends = 0
        estimated_cost = 0.0
        
        for result in results:
            try:
                campaign_message = pending_messages.get(recipient_phone=result['recipient'])
                
                if result['success']:
                    campaign_message.status = 'sent'
                    campaign_message.twilio_sid = result.get('message_sid')
                    campaign_message.sent_at = timezone.now()
                    successful_sends += 1
                    estimated_cost += 0.005  # Approximate Twilio cost per message
                else:
                    campaign_message.status = 'failed'
                    campaign_message.error_message = result.get('error')
                    failed_sends += 1
                
                campaign_message.save()
                
            except CampaignMessage.DoesNotExist:
                logger.warning(f"Campaign message not found for recipient: {result['recipient']}")
        
        return {
            'service': 'Twilio',
            'total_processed': len(results),
            'successful_sends': successful_sends,
            'failed_sends': failed_sends,
            'estimated_cost': estimated_cost,
            'details': results
        }
    
    def _update_campaign_analytics(self, campaign: Campaign):
        """Update or create campaign analytics"""
        analytics, created = CampaignAnalytics.objects.get_or_create(
            campaign=campaign,
            defaults={
                'total_recipients': 0,
                'messages_sent': 0,
                'messages_delivered': 0,
                'messages_read': 0,
                'messages_failed': 0,
            }
        )
        
        # Update analytics based on campaign messages
        analytics.update_analytics()
    
    def get_campaign_status(self, campaign_id: int) -> Dict[str, Any]:
        """Get real-time status of a running campaign"""
        try:
            campaign = Campaign.objects.get(id=campaign_id)
            analytics = getattr(campaign, 'analytics', None)
            
            return {
                'success': True,
                'campaign_id': campaign.id,
                'campaign_name': campaign.name,
                'status': campaign.status,
                'started_at': campaign.started_at,
                'completed_at': campaign.completed_at,
                'total_recipients': campaign.get_total_recipients(),
                'messages_sent': campaign.get_sent_count(),
                'messages_failed': campaign.get_failed_count(),
                'analytics': {
                    'delivery_rate': analytics.delivery_rate if analytics else 0,
                    'read_rate': analytics.read_rate if analytics else 0,
                    'cost_estimate': float(analytics.cost_estimate) if analytics else 0
                } if analytics else None
            }
            
        except Campaign.DoesNotExist:
            return {
                'success': False,
                'error': f'Campaign with ID {campaign_id} not found'
            }
    
    def cancel_campaign(self, campaign_id: int) -> Dict[str, Any]:
        """Cancel a running campaign"""
        try:
            campaign = Campaign.objects.get(id=campaign_id)
            
            if campaign.status != 'running':
                return {
                    'success': False,
                    'error': f'Campaign is not running (current status: {campaign.status})'
                }
            
            campaign.status = 'cancelled'
            campaign.completed_at = timezone.now()
            campaign.save()
            
            # Update any pending messages to cancelled
            campaign.campaign_messages.filter(status='pending').update(
                status='failed',
                error_message='Campaign cancelled by user'
            )
            
            return {
                'success': True,
                'message': f'Campaign {campaign.name} has been cancelled'
            }
            
        except Campaign.DoesNotExist:
            return {
                'success': False,
                'error': f'Campaign with ID {campaign_id} not found'
            }


class CampaignSchedulerService:
    """Service to handle scheduled campaigns"""
    
    def __init__(self):
        self.execution_service = CampaignExecutionService()
    
    def check_and_execute_scheduled_campaigns(self):
        """Check for scheduled campaigns and execute them"""
        now = timezone.now()
        scheduled_campaigns = Campaign.objects.filter(
            status='scheduled',
            scheduled_at__lte=now
        )
        
        results = []
        
        for campaign in scheduled_campaigns:
            logger.info(f"Executing scheduled campaign: {campaign.name}")
            result = self.execution_service.execute_campaign(
                campaign.id,
                use_whatsapp_web=True  # Default to free WhatsApp Web
            )
            results.append(result)
        
        return results
