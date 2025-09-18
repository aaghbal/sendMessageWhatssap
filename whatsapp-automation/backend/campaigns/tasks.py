from celery import shared_task
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Campaign, CampaignMessage, CampaignAnalytics
from whatsapp_messages.services import TwilioWhatsAppService
from whatsapp_messages.models import SentMessage
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task(bind=True)
def send_campaign_messages(self, campaign_id):
    """
    Celery task to send campaign messages
    """
    try:
        campaign = Campaign.objects.get(id=campaign_id)
        twilio_service = TwilioWhatsAppService()
        
        # Update campaign status
        campaign.status = 'running'
        campaign.started_at = timezone.now()
        campaign.save()
        
        # Get all recipients
        recipients = []
        
        # Add individual phone numbers
        for phone in campaign.target_phones.filter(is_active=True):
            recipients.append({
                'phone': phone.full_phone_number,
                'name': phone.name
            })
        
        # Add phone numbers from groups
        for group in campaign.target_groups.all():
            for phone in group.phone_numbers.filter(is_active=True):
                recipients.append({
                    'phone': phone.full_phone_number,
                    'name': phone.name
                })
        
        # Remove duplicates
        unique_recipients = []
        seen_phones = set()
        for recipient in recipients:
            if recipient['phone'] not in seen_phones:
                unique_recipients.append(recipient)
                seen_phones.add(recipient['phone'])
        
        # Create campaign messages
        campaign_messages = []
        for recipient in unique_recipients:
            campaign_message = CampaignMessage(
                campaign=campaign,
                recipient_phone=recipient['phone'],
                recipient_name=recipient['name'],
                message_content=campaign.message_template.content,
                status='pending'
            )
            campaign_messages.append(campaign_message)
        
        CampaignMessage.objects.bulk_create(campaign_messages)
        
        # Send messages
        sent_count = 0
        failed_count = 0
        
        for campaign_message in CampaignMessage.objects.filter(campaign=campaign):
            # Send message using Twilio
            result = twilio_service.send_message(
                campaign_message.recipient_phone,
                campaign_message.message_content,
                campaign.message_template.media_url
            )
            
            if result['success']:
                campaign_message.status = 'sent'
                campaign_message.twilio_sid = result['message_sid']
                campaign_message.sent_at = timezone.now()
                sent_count += 1
                
                # Also create a SentMessage record
                SentMessage.objects.create(
                    user=campaign.user,
                    recipient_phone=campaign_message.recipient_phone,
                    recipient_name=campaign_message.recipient_name,
                    message_content=campaign_message.message_content,
                    template_used=campaign.message_template,
                    status='sent',
                    twilio_sid=result['message_sid']
                )
            else:
                campaign_message.status = 'failed'
                campaign_message.error_message = result['error']
                failed_count += 1
            
            campaign_message.save()
            
            # Update task progress
            progress = (sent_count + failed_count) / len(unique_recipients) * 100
            self.update_state(
                state='PROGRESS',
                meta={'progress': progress, 'sent': sent_count, 'failed': failed_count}
            )
        
        # Update campaign status
        campaign.status = 'completed'
        campaign.completed_at = timezone.now()
        campaign.save()
        
        # Update analytics
        analytics, created = CampaignAnalytics.objects.get_or_create(campaign=campaign)
        analytics.update_analytics()
        
        logger.info(f"Campaign {campaign_id} completed. Sent: {sent_count}, Failed: {failed_count}")
        
        return {
            'status': 'completed',
            'sent_count': sent_count,
            'failed_count': failed_count,
            'total_recipients': len(unique_recipients)
        }
        
    except Campaign.DoesNotExist:
        logger.error(f"Campaign {campaign_id} not found")
        return {'status': 'error', 'message': 'Campaign not found'}
        
    except Exception as error:
        logger.error(f"Error sending campaign messages: {str(error)}")
        
        # Update campaign status to failed
        try:
            campaign = Campaign.objects.get(id=campaign_id)
            campaign.status = 'failed'
            campaign.save()
        except:
            pass
        
        return {'status': 'error', 'message': str(error)}


@shared_task
def update_message_statuses():
    """
    Periodic task to update message statuses from Twilio
    """
    twilio_service = TwilioWhatsAppService()
    
    # Get recent messages that might have status updates
    recent_messages = SentMessage.objects.filter(
        status__in=['sent', 'pending'],
        twilio_sid__isnull=False,
        sent_at__gte=timezone.now() - timezone.timedelta(hours=24)
    )
    
    updated_count = 0
    
    for message in recent_messages:
        try:
            status_info = twilio_service.get_message_status(message.twilio_sid)
            
            if status_info['success']:
                old_status = message.status
                new_status = status_info['status']
                
                # Map Twilio statuses to our statuses
                status_mapping = {
                    'delivered': 'delivered',
                    'read': 'read',
                    'failed': 'failed',
                    'undelivered': 'failed'
                }
                
                if new_status in status_mapping and old_status != status_mapping[new_status]:
                    message.status = status_mapping[new_status]
                    
                    if new_status in ['delivered', 'read']:
                        message.delivered_at = timezone.now()
                    
                    if status_info.get('error_message'):
                        message.error_message = status_info['error_message']
                    
                    message.save()
                    updated_count += 1
                    
        except Exception as error:
            logger.error(f"Error updating message status for {message.id}: {str(error)}")
    
    # Also update campaign messages
    recent_campaign_messages = CampaignMessage.objects.filter(
        status__in=['sent', 'pending'],
        twilio_sid__isnull=False,
        sent_at__gte=timezone.now() - timezone.timedelta(hours=24)
    )
    
    for message in recent_campaign_messages:
        try:
            status_info = twilio_service.get_message_status(message.twilio_sid)
            
            if status_info['success']:
                old_status = message.status
                new_status = status_info['status']
                
                status_mapping = {
                    'delivered': 'delivered',
                    'read': 'read',
                    'failed': 'failed',
                    'undelivered': 'failed'
                }
                
                if new_status in status_mapping and old_status != status_mapping[new_status]:
                    message.status = status_mapping[new_status]
                    
                    if new_status in ['delivered', 'read']:
                        message.delivered_at = timezone.now()
                    
                    if status_info.get('error_message'):
                        message.error_message = status_info['error_message']
                    
                    message.save()
                    
                    # Update campaign analytics
                    analytics, created = CampaignAnalytics.objects.get_or_create(
                        campaign=message.campaign
                    )
                    analytics.update_analytics()
                    
        except Exception as error:
            logger.error(f"Error updating campaign message status for {message.id}: {str(error)}")
    
    logger.info(f"Updated {updated_count} message statuses")
    return {'updated_count': updated_count}


@shared_task
def schedule_campaign(campaign_id, scheduled_time):
    """
    Task to schedule campaign execution
    """
    try:
        campaign = Campaign.objects.get(id=campaign_id)
        
        if campaign.status == 'scheduled':
            # Execute the campaign
            send_campaign_messages.delay(campaign_id)
            logger.info(f"Scheduled campaign {campaign_id} started execution")
            return {'status': 'started', 'campaign_id': campaign_id}
        else:
            logger.warning(f"Campaign {campaign_id} is not in scheduled status")
            return {'status': 'skipped', 'reason': 'Campaign not scheduled'}
            
    except Campaign.DoesNotExist:
        logger.error(f"Scheduled campaign {campaign_id} not found")
        return {'status': 'error', 'message': 'Campaign not found'}
