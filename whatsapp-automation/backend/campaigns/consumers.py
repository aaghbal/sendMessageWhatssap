import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

User = get_user_model()


class CampaignConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time campaign updates"""
    
    async def connect(self):
        self.user = self.scope["user"]
        
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return
        
        # Join user-specific group
        self.user_group_name = f"user_{self.user.id}"
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        if hasattr(self, 'user_group_name'):
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            if message_type == 'subscribe_campaign':
                campaign_id = text_data_json.get('campaign_id')
                await self.subscribe_to_campaign(campaign_id)
            elif message_type == 'unsubscribe_campaign':
                campaign_id = text_data_json.get('campaign_id')
                await self.unsubscribe_from_campaign(campaign_id)
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON'
            }))
    
    async def subscribe_to_campaign(self, campaign_id):
        """Subscribe to specific campaign updates"""
        if await self.user_owns_campaign(campaign_id):
            campaign_group_name = f"campaign_{campaign_id}"
            await self.channel_layer.group_add(
                campaign_group_name,
                self.channel_name
            )
            
            await self.send(text_data=json.dumps({
                'type': 'subscription_confirmed',
                'campaign_id': campaign_id
            }))
    
    async def unsubscribe_from_campaign(self, campaign_id):
        """Unsubscribe from specific campaign updates"""
        campaign_group_name = f"campaign_{campaign_id}"
        await self.channel_layer.group_discard(
            campaign_group_name,
            self.channel_name
        )
        
        await self.send(text_data=json.dumps({
            'type': 'unsubscription_confirmed',
            'campaign_id': campaign_id
        }))
    
    @database_sync_to_async
    def user_owns_campaign(self, campaign_id):
        """Check if user owns the campaign"""
        from .models import Campaign
        try:
            campaign = Campaign.objects.get(id=campaign_id, user=self.user)
            return True
        except Campaign.DoesNotExist:
            return False
    
    async def campaign_update(self, event):
        """Send campaign update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'campaign_update',
            'campaign_id': event['campaign_id'],
            'status': event['status'],
            'progress': event.get('progress'),
            'sent_count': event.get('sent_count'),
            'failed_count': event.get('failed_count'),
            'message': event.get('message')
        }))
    
    async def message_status_update(self, event):
        """Send message status update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'message_status_update',
            'message_id': event['message_id'],
            'status': event['status'],
            'timestamp': event['timestamp']
        }))


class NotificationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for general notifications"""
    
    async def connect(self):
        self.user = self.scope["user"]
        
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return
        
        # Join user-specific notification group
        self.notification_group_name = f"notifications_{self.user.id}"
        await self.channel_layer.group_add(
            self.notification_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        if hasattr(self, 'notification_group_name'):
            await self.channel_layer.group_discard(
                self.notification_group_name,
                self.channel_name
            )
    
    async def notification(self, event):
        """Send notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'title': event['title'],
            'message': event['message'],
            'level': event.get('level', 'info'),
            'timestamp': event['timestamp']
        }))
