from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from .models import MessageTemplate, SentMessage
from .serializers import MessageTemplateSerializer, SentMessageSerializer, SendMessageSerializer
from .services import TwilioWhatsAppService


class MessageTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for managing message templates"""
    serializer_class = MessageTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = MessageTemplate.objects.filter(user=self.request.user)
        
        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(content__icontains=search)
            )
        
        # Filter by message type
        message_type = self.request.query_params.get('message_type', None)
        if message_type:
            queryset = queryset.filter(message_type=message_type)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle active status of a message template"""
        template = self.get_object()
        template.is_active = not template.is_active
        template.save()
        
        return Response({
            'id': template.id,
            'is_active': template.is_active,
            'message': f'Template {"activated" if template.is_active else "deactivated"}'
        })
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate a message template"""
        template = self.get_object()
        
        # Create a copy
        new_template = MessageTemplate.objects.create(
            user=template.user,
            name=f"{template.name} (Copy)",
            message_type=template.message_type,
            content=template.content,
            media_url=template.media_url,
            is_active=template.is_active
        )
        
        serializer = self.get_serializer(new_template)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SentMessageViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing sent messages"""
    serializer_class = SentMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = SentMessage.objects.filter(user=self.request.user)
        
        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(recipient_phone__icontains=search) |
                Q(recipient_name__icontains=search) |
                Q(message_content__icontains=search)
            )
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        
        if date_from:
            queryset = queryset.filter(sent_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(sent_at__date__lte=date_to)
        
        return queryset.order_by('-sent_at')
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get message analytics"""
        queryset = self.get_queryset()
        
        total_messages = queryset.count()
        sent_messages = queryset.filter(status__in=['sent', 'delivered', 'read']).count()
        delivered_messages = queryset.filter(status__in=['delivered', 'read']).count()
        read_messages = queryset.filter(status='read').count()
        failed_messages = queryset.filter(status='failed').count()
        
        # Calculate rates
        delivery_rate = (delivered_messages / sent_messages * 100) if sent_messages > 0 else 0
        read_rate = (read_messages / sent_messages * 100) if sent_messages > 0 else 0
        failure_rate = (failed_messages / total_messages * 100) if total_messages > 0 else 0
        
        return Response({
            'total_messages': total_messages,
            'sent_messages': sent_messages,
            'delivered_messages': delivered_messages,
            'read_messages': read_messages,
            'failed_messages': failed_messages,
            'delivery_rate': round(delivery_rate, 2),
            'read_rate': round(read_rate, 2),
            'failure_rate': round(failure_rate, 2)
        })
    
    @action(detail=False, methods=['post'])
    def send_message(self, request):
        """Send individual WhatsApp message"""
        serializer = SendMessageSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        twilio_service = TwilioWhatsAppService()
        
        # Get template if provided
        template = None
        if data.get('template_id'):
            template = MessageTemplate.objects.get(
                id=data['template_id'],
                user=request.user
            )
        
        # Send message
        result = twilio_service.send_message(
            data['recipient_phone'],
            data['message_content'],
            template.media_url if template and template.media_url else None
        )
        
        # Create SentMessage record
        sent_message = SentMessage.objects.create(
            user=request.user,
            recipient_phone=data['recipient_phone'],
            recipient_name=data.get('recipient_name', ''),
            message_content=data['message_content'],
            template_used=template,
            status='sent' if result['success'] else 'failed',
            twilio_sid=result.get('message_sid'),
            error_message=result.get('error') if not result['success'] else None
        )
        
        # Return response
        response_data = {
            'message_id': sent_message.id,
            'success': result['success'],
            'status': sent_message.status
        }
        
        if not result['success']:
            response_data['error'] = result['error']
        
        return Response(response_data, status=status.HTTP_201_CREATED if result['success'] else status.HTTP_400_BAD_REQUEST)
