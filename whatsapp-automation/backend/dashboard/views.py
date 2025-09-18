from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Q
from datetime import datetime, timedelta
from campaigns.models import Campaign, CampaignAnalytics
from contacts.models import PhoneNumber
from whatsapp_messages.models import MessageTemplate, SentMessage


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Get dashboard statistics"""
    user = request.user
    today = datetime.now().date()
    month_start = today.replace(day=1)
    
    # Basic counts
    total_contacts = PhoneNumber.objects.filter(user=user).count()
    total_templates = MessageTemplate.objects.filter(user=user).count()
    total_campaigns = Campaign.objects.filter(user=user).count()
    active_campaigns = Campaign.objects.filter(
        user=user, 
        status__in=['running', 'scheduled']
    ).count()
    
    # Messages sent today and this month
    messages_today = SentMessage.objects.filter(
        user=user,
        sent_at__date=today
    ).count()
    
    messages_this_month = SentMessage.objects.filter(
        user=user,
        sent_at__date__gte=month_start
    ).count()
    
    # Calculate success rate for this month
    successful_messages = SentMessage.objects.filter(
        user=user,
        sent_at__date__gte=month_start,
        status__in=['delivered', 'read']
    ).count()
    
    success_rate = 0
    if messages_this_month > 0:
        success_rate = (successful_messages / messages_this_month) * 100
    
    # Recent campaigns (last 5)
    recent_campaigns = Campaign.objects.filter(user=user).order_by('-created_at')[:5]
    recent_campaigns_data = []
    
    for campaign in recent_campaigns:
        recent_campaigns_data.append({
            'id': campaign.id,
            'name': campaign.name,
            'description': campaign.description,
            'status': campaign.status,
            'created_at': campaign.created_at,
            'updated_at': campaign.updated_at,
        })
    
    return Response({
        'total_contacts': total_contacts,
        'total_templates': total_templates,
        'total_campaigns': total_campaigns,
        'active_campaigns': active_campaigns,
        'messages_sent_today': messages_today,
        'messages_sent_this_month': messages_this_month,
        'success_rate_this_month': success_rate,
        'recent_campaigns': recent_campaigns_data,
    })
