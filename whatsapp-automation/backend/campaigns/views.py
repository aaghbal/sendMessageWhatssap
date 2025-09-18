from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Campaign, CampaignMessage, CampaignAnalytics
from .serializers import (
    CampaignSerializer, 
    CampaignCreateSerializer,
    CampaignStatusUpdateSerializer,
    CampaignMessageSerializer,
    CampaignAnalyticsSerializer
)
from .tasks import send_campaign_messages, schedule_campaign


class CampaignViewSet(viewsets.ModelViewSet):
    """ViewSet for managing campaigns"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Campaign.objects.filter(user=self.request.user)
        
        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CampaignCreateSerializer
        elif self.action == 'update_status':
            return CampaignStatusUpdateSerializer
        return CampaignSerializer
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start a campaign using WhatsApp Web or Twilio"""
        campaign = self.get_object()
        
        if campaign.status not in ['draft', 'scheduled']:
            return Response({
                'error': 'Campaign can only be started from draft or scheduled status'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if campaign has recipients
        if campaign.get_total_recipients() == 0:
            return Response({
                'error': 'Campaign must have at least one recipient'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get service preference (default to WhatsApp Web for free messaging)
        use_whatsapp_web = request.data.get('use_whatsapp_web', True)
        
        # Import and use the new campaign execution service
        from .services import CampaignExecutionService
        execution_service = CampaignExecutionService()
        
        # Execute campaign directly (can be moved to Celery task if needed)
        result = execution_service.execute_campaign(campaign.id, use_whatsapp_web)
        
        if result['success']:
            # Send WebSocket notification
            self.send_campaign_update(campaign.id, 'completed', 'Campaign completed successfully')
            
            return Response({
                'message': 'Campaign executed successfully',
                'service_used': result.get('service_used', 'Unknown'),
                'total_recipients': result.get('total_recipients', 0),
                'campaign_id': campaign.id,
                'results': result.get('results', {})
            })
        else:
            # Send WebSocket notification
            self.send_campaign_update(campaign.id, 'failed', f'Campaign failed: {result.get("error", "Unknown error")}')
            
            return Response({
                'error': result.get('error', 'Campaign execution failed'),
                'campaign_id': campaign.id
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def schedule(self, request, pk=None):
        """Schedule a campaign"""
        campaign = self.get_object()
        scheduled_time = request.data.get('scheduled_at')
        
        if not scheduled_time:
            return Response({
                'error': 'scheduled_at is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if campaign.status != 'draft':
            return Response({
                'error': 'Only draft campaigns can be scheduled'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Parse scheduled time
        from datetime import datetime
        try:
            scheduled_datetime = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
        except ValueError:
            return Response({
                'error': 'Invalid datetime format'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if scheduled_datetime <= timezone.now():
            return Response({
                'error': 'Scheduled time must be in the future'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update campaign
        campaign.scheduled_at = scheduled_datetime
        campaign.status = 'scheduled'
        campaign.save()
        
        # Schedule the task
        schedule_campaign.apply_async(
            args=[campaign.id, scheduled_time],
            eta=scheduled_datetime
        )
        
        return Response({
            'message': 'Campaign scheduled successfully',
            'scheduled_at': scheduled_datetime.isoformat()
        })
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a campaign"""
        campaign = self.get_object()
        
        if campaign.status not in ['scheduled', 'running']:
            return Response({
                'error': 'Only scheduled or running campaigns can be cancelled'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        campaign.status = 'cancelled'
        campaign.save()
        
        # Send WebSocket notification
        self.send_campaign_update(campaign.id, 'cancelled', 'Campaign cancelled')
        
        return Response({
            'message': 'Campaign cancelled successfully'
        })
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get campaign messages"""
        campaign = self.get_object()
        messages = campaign.campaign_messages.all()
        
        # Filter by status if provided
        status_filter = request.query_params.get('status', None)
        if status_filter:
            messages = messages.filter(status=status_filter)
        
        # Apply pagination
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = CampaignMessageSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = CampaignMessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get campaign analytics"""
        campaign = self.get_object()
        
        # Get or create analytics
        analytics, created = CampaignAnalytics.objects.get_or_create(campaign=campaign)
        if created or analytics.updated_at < timezone.now() - timezone.timedelta(minutes=5):
            analytics.update_analytics()
        
        serializer = CampaignAnalyticsSerializer(analytics)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate a campaign"""
        campaign = self.get_object()
        
        # Create a copy
        new_campaign = Campaign.objects.create(
            user=campaign.user,
            name=f"{campaign.name} (Copy)",
            description=campaign.description,
            message_template=campaign.message_template,
            status='draft'
        )
        
        # Copy target groups and phones
        new_campaign.target_groups.set(campaign.target_groups.all())
        new_campaign.target_phones.set(campaign.target_phones.all())
        
        serializer = CampaignSerializer(new_campaign)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def start_whatsapp_web(self, request, pk=None):
        """Start a campaign specifically using WhatsApp Web (free method from sc.py)"""
        campaign = self.get_object()
        
        if campaign.status not in ['draft', 'scheduled']:
            return Response({
                'error': 'Campaign can only be started from draft or scheduled status'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if campaign.get_total_recipients() == 0:
            return Response({
                'error': 'Campaign must have at least one recipient'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Import and use WhatsApp Web service
        from .services import CampaignExecutionService
        execution_service = CampaignExecutionService()
        
        # Execute with WhatsApp Web specifically
        result = execution_service.execute_campaign(campaign.id, use_whatsapp_web=True)
        
        if result['success']:
            self.send_campaign_update(campaign.id, 'completed', 'WhatsApp Web campaign completed')
            
            return Response({
                'message': 'WhatsApp Web campaign executed successfully',
                'service_used': 'WhatsApp Web (Free)',
                'total_recipients': result.get('total_recipients', 0),
                'successful_sends': result['results'].get('successful_sends', 0),
                'failed_sends': result['results'].get('failed_sends', 0),
                'cost': 0.00,  # Free with WhatsApp Web
                'campaign_id': campaign.id
            })
        else:
            self.send_campaign_update(campaign.id, 'failed', f'WhatsApp Web campaign failed: {result.get("error")}')
            
            return Response({
                'error': result.get('error', 'WhatsApp Web campaign execution failed'),
                'suggestion': 'Make sure WhatsApp Web session is active. Try: python manage.py setup_whatsapp',
                'campaign_id': campaign.id
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def start_twilio(self, request, pk=None):
        """Start a campaign specifically using Twilio (paid API)"""
        campaign = self.get_object()
        
        if campaign.status not in ['draft', 'scheduled']:
            return Response({
                'error': 'Campaign can only be started from draft or scheduled status'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if campaign.get_total_recipients() == 0:
            return Response({
                'error': 'Campaign must have at least one recipient'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Import and use Twilio service
        from .services import CampaignExecutionService
        execution_service = CampaignExecutionService()
        
        # Execute with Twilio specifically
        result = execution_service.execute_campaign(campaign.id, use_whatsapp_web=False)
        
        if result['success']:
            self.send_campaign_update(campaign.id, 'completed', 'Twilio campaign completed')
            
            return Response({
                'message': 'Twilio campaign executed successfully',
                'service_used': 'Twilio API (Paid)',
                'total_recipients': result.get('total_recipients', 0),
                'successful_sends': result['results'].get('successful_sends', 0),
                'failed_sends': result['results'].get('failed_sends', 0),
                'estimated_cost': result['results'].get('estimated_cost', 0),
                'campaign_id': campaign.id
            })
        else:
            self.send_campaign_update(campaign.id, 'failed', f'Twilio campaign failed: {result.get("error")}')
            
            return Response({
                'error': result.get('error', 'Twilio campaign execution failed'),
                'campaign_id': campaign.id
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def setup_whatsapp_web(self, request):
        """Setup WhatsApp Web session for campaigns"""
        try:
            from whatsapp_messages.whatsapp_web_service import WhatsAppWebService
            service = WhatsAppWebService()
            
            success = service.setup_session()
            
            if success:
                return Response({
                    'success': True,
                    'message': 'WhatsApp Web session setup completed! You can now run free campaigns.',
                    'next_steps': [
                        'Create a new campaign',
                        'Add recipients and message template',
                        'Click "Start WhatsApp Web Campaign" for free messaging'
                    ]
                })
            else:
                return Response({
                    'success': False,
                    'error': 'Failed to setup WhatsApp Web session',
                    'troubleshooting': [
                        'Make sure Chrome browser is installed',
                        'Ensure good internet connection',
                        'Try running: python manage.py setup_whatsapp'
                    ]
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Setup failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def whatsapp_web_status(self, request):
        """Check WhatsApp Web session status"""
        try:
            from whatsapp_messages.whatsapp_web_service import WhatsAppWebService
            import os
            
            service = WhatsAppWebService()
            session_path = os.path.join(service.session_dir, 'Default')
            session_exists = os.path.exists(session_path)
            
            return Response({
                'session_active': session_exists,
                'status': 'Ready for free campaigns' if session_exists else 'Needs setup',
                'recommendation': 'You can run campaigns for free!' if session_exists else 'Setup WhatsApp Web session first',
                'setup_command': 'python manage.py setup_whatsapp' if not session_exists else None
            })
            
        except Exception as e:
            return Response({
                'error': f'Status check failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def send_campaign_update(self, campaign_id, status, message):
        """Send campaign update via WebSocket"""
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"campaign_{campaign_id}",
            {
                'type': 'campaign_update',
                'campaign_id': campaign_id,
                'status': status,
                'message': message
            }
        )


class CampaignMessageViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing campaign messages"""
    serializer_class = CampaignMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Only show messages from campaigns owned by the user
        return CampaignMessage.objects.filter(campaign__user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent campaign messages"""
        messages = self.get_queryset().order_by('-created_at')[:20]
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)
