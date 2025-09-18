from twilio.rest import Client
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class TwilioWhatsAppService:
    """Service class for Twilio WhatsApp integration"""
    
    def __init__(self):
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self.from_phone = settings.TWILIO_PHONE_NUMBER
    
    def send_message(self, to_phone, message_content, media_url=None):
        """
        Send a WhatsApp message using Twilio
        
        Args:
            to_phone (str): Recipient phone number with country code
            message_content (str): Message content
            media_url (str, optional): URL for media attachment
            
        Returns:
            dict: Result with success status and message details
        """
        try:
            # Format phone number for WhatsApp
            if not to_phone.startswith('whatsapp:'):
                to_phone = f'whatsapp:{to_phone}'
            
            from_phone = f'whatsapp:{self.from_phone}'
            
            # Prepare message parameters
            message_params = {
                'from_': from_phone,
                'to': to_phone,
                'body': message_content
            }
            
            # Add media if provided
            if media_url:
                message_params['media_url'] = [media_url]
            
            # Send message
            message = self.client.messages.create(**message_params)
            
            logger.info(f"WhatsApp message sent successfully. SID: {message.sid}")
            
            return {
                'success': True,
                'message_sid': message.sid,
                'status': message.status,
                'error': None
            }
            
        except Exception as error:
            logger.error(f"Failed to send WhatsApp message: {str(error)}")
            return {
                'success': False,
                'message_sid': None,
                'status': 'failed',
                'error': str(error)
            }
    
    def get_message_status(self, message_sid):
        """
        Get the current status of a sent message
        
        Args:
            message_sid (str): Twilio message SID
            
        Returns:
            dict: Message status information
        """
        try:
            message = self.client.messages(message_sid).fetch()
            
            return {
                'success': True,
                'status': message.status,
                'error_code': message.error_code,
                'error_message': message.error_message,
                'date_sent': message.date_sent,
                'date_updated': message.date_updated
            }
            
        except Exception as error:
            logger.error(f"Failed to fetch message status: {str(error)}")
            return {
                'success': False,
                'status': 'unknown',
                'error': str(error)
            }
    
    def validate_phone_number(self, phone_number):
        """
        Validate phone number format for WhatsApp
        
        Args:
            phone_number (str): Phone number to validate
            
        Returns:
            dict: Validation result
        """
        try:
            # Use Twilio Lookup API to validate phone number
            phone_number_info = self.client.lookups.phone_numbers(phone_number).fetch()
            
            return {
                'valid': True,
                'formatted_number': phone_number_info.phone_number,
                'country_code': phone_number_info.country_code,
                'carrier': phone_number_info.carrier.get('name') if phone_number_info.carrier else None
            }
            
        except Exception as error:
            logger.error(f"Phone number validation failed: {str(error)}")
            return {
                'valid': False,
                'error': str(error)
            }
    
    def send_bulk_messages(self, recipients, message_content, media_url=None):
        """
        Send bulk WhatsApp messages
        
        Args:
            recipients (list): List of recipient phone numbers
            message_content (str): Message content
            media_url (str, optional): URL for media attachment
            
        Returns:
            list: List of results for each message
        """
        results = []
        
        for phone_number in recipients:
            result = self.send_message(phone_number, message_content, media_url)
            result['recipient'] = phone_number
            results.append(result)
            
            # Add small delay to avoid rate limiting
            import time
            time.sleep(0.5)
        
        return results
    
    def handle_webhook(self, request_data):
        """
        Handle Twilio webhook for message status updates
        
        Args:
            request_data (dict): Webhook data from Twilio
            
        Returns:
            dict: Processed webhook data
        """
        try:
            message_sid = request_data.get('MessageSid')
            message_status = request_data.get('MessageStatus')
            error_code = request_data.get('ErrorCode')
            error_message = request_data.get('ErrorMessage')
            
            return {
                'message_sid': message_sid,
                'status': message_status,
                'error_code': error_code,
                'error_message': error_message,
                'timestamp': timezone.now()
            }
            
        except Exception as error:
            logger.error(f"Failed to process webhook: {str(error)}")
            return {
                'error': str(error)
            }
