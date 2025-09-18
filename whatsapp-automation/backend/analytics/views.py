from django.utils import timezone
from django.db.models import Count, Q, Avg
from django.db.models.functions import TruncDate, TruncHour, Extract
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import datetime, timedelta
from campaigns.models import Campaign, CampaignMessage
from whatsapp_messages.models import SentMessage
from contacts.models import PhoneNumber


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_overview(request):
    """
    Get comprehensive analytics overview
    """
    user = request.user
    date_range = request.GET.get('date_range', '7days')
    
    # Calculate date range
    now = timezone.now()
    if date_range == '7days':
        start_date = now - timedelta(days=7)
    elif date_range == '30days':
        start_date = now - timedelta(days=30)
    elif date_range == '90days':
        start_date = now - timedelta(days=90)
    else:
        start_date = now - timedelta(days=7)
    
    # Overview statistics
    total_campaigns = Campaign.objects.filter(user=user).count()
    active_campaigns = Campaign.objects.filter(user=user, status='running').count()
    
    # Message statistics in the selected date range
    sent_messages = SentMessage.objects.filter(user=user, sent_at__gte=start_date)
    campaign_messages = CampaignMessage.objects.filter(
        campaign__user=user, 
        created_at__gte=start_date
    )
    
    # Combine both message types for total counts
    total_sent_messages = sent_messages.count() + campaign_messages.filter(
        status__in=['sent', 'delivered', 'read']
    ).count()
    
    total_failed_messages = sent_messages.filter(status='failed').count() + \
                          campaign_messages.filter(status='failed').count()
    
    successful_messages = total_sent_messages - total_failed_messages
    success_rate = (successful_messages / total_sent_messages * 100) if total_sent_messages > 0 else 0
    
    # Daily statistics for the date range
    daily_stats = []
    for i in range((start_date.date() - now.date()).days, 1):
        current_date = now.date() + timedelta(days=i)
        
        # Messages sent on this day
        daily_sent = sent_messages.filter(sent_at__date=current_date).count()
        daily_campaign = campaign_messages.filter(
            created_at__date=current_date,
            status__in=['sent', 'delivered', 'read']
        ).count()
        
        # Failed messages on this day
        daily_failed_sent = sent_messages.filter(sent_at__date=current_date, status='failed').count()
        daily_failed_campaign = campaign_messages.filter(
            created_at__date=current_date,
            status='failed'
        ).count()
        
        total_daily = daily_sent + daily_campaign
        failed_daily = daily_failed_sent + daily_failed_campaign
        success_daily = total_daily - failed_daily
        daily_success_rate = (success_daily / total_daily * 100) if total_daily > 0 else 0
        
        daily_stats.append({
            'date': current_date.isoformat(),
            'messages_sent': total_daily,
            'success_rate': daily_success_rate
        })
    
    # Campaign performance
    completed_campaigns = Campaign.objects.filter(
        user=user,
        status='completed',
        completed_at__gte=start_date
    ).select_related()
    
    campaign_performance = []
    for campaign in completed_campaigns:
        campaign_messages_qs = campaign.campaign_messages.all()
        total_msgs = campaign_messages_qs.count()
        successful_msgs = campaign_messages_qs.filter(
            status__in=['sent', 'delivered', 'read']
        ).count()
        campaign_success_rate = (successful_msgs / total_msgs * 100) if total_msgs > 0 else 0
        
        campaign_performance.append({
            'campaign_name': campaign.name,
            'messages_sent': total_msgs,
            'success_rate': campaign_success_rate,
            'completion_date': campaign.completed_at.isoformat() if campaign.completed_at else None
        })
    
    # Hourly distribution (for peak hours analysis)
    hourly_distribution = []
    
    # Get hourly stats from sent messages
    sent_hourly = sent_messages.annotate(
        hour=Extract('sent_at', 'hour')
    ).values('hour').annotate(count=Count('id'))
    
    # Get hourly stats from campaign messages
    campaign_hourly = campaign_messages.filter(
        status__in=['sent', 'delivered', 'read']
    ).annotate(
        hour=Extract('created_at', 'hour')
    ).values('hour').annotate(count=Count('id'))
    
    # Combine hourly data
    hourly_data = {}
    try:
        for entry in sent_hourly:
            hour = int(entry['hour']) if entry['hour'] is not None else 0
            hourly_data[hour] = hourly_data.get(hour, 0) + entry['count']
        
        for entry in campaign_hourly:
            hour = int(entry['hour']) if entry['hour'] is not None else 0
            hourly_data[hour] = hourly_data.get(hour, 0) + entry['count']
    except Exception as e:
        # If hourly data fails, provide empty data
        print(f"Error processing hourly data: {e}")
        hourly_data = {}
    
    # Convert to list format
    for hour in range(24):
        if hour in hourly_data and hourly_data[hour] > 0:
            hourly_distribution.append({
                'hour': hour,
                'message_count': hourly_data[hour]
            })
    
    # Sort by message count and take top hours only
    hourly_distribution.sort(key=lambda x: x['message_count'], reverse=True)
    hourly_distribution = hourly_distribution[:9]  # Top 9 hours
    
    # Messages today and this month
    today = now.date()
    start_of_month = today.replace(day=1)
    
    messages_today = sent_messages.filter(sent_at__date=today).count() + \
                    campaign_messages.filter(
                        created_at__date=today,
                        status__in=['sent', 'delivered', 'read']
                    ).count()
    
    messages_this_month = sent_messages.filter(sent_at__date__gte=start_of_month).count() + \
                         campaign_messages.filter(
                             created_at__date__gte=start_of_month,
                             status__in=['sent', 'delivered', 'read']
                         ).count()
    
    # Success rate this month
    failed_this_month = sent_messages.filter(
        sent_at__date__gte=start_of_month, 
        status='failed'
    ).count() + campaign_messages.filter(
        created_at__date__gte=start_of_month,
        status='failed'
    ).count()
    
    success_rate_this_month = ((messages_this_month - failed_this_month) / messages_this_month * 100) \
                             if messages_this_month > 0 else 0
    
    return Response({
        'overview': {
            'total_messages': total_sent_messages,
            'successful_messages': successful_messages,
            'failed_messages': total_failed_messages,
            'success_rate': success_rate,
            'total_campaigns': total_campaigns,
            'active_campaigns': active_campaigns,
            'messages_sent_today': messages_today,
            'messages_sent_this_month': messages_this_month,
            'success_rate_this_month': success_rate_this_month
        },
        'daily_stats': daily_stats,
        'campaign_performance': campaign_performance,
        'hourly_distribution': hourly_distribution
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def campaign_analytics_detail(request, campaign_id):
    """
    Get detailed analytics for a specific campaign
    """
    try:
        campaign = Campaign.objects.get(id=campaign_id, user=request.user)
        messages = campaign.campaign_messages.all()
        
        # Basic stats
        total_messages = messages.count()
        sent_messages = messages.filter(status__in=['sent', 'delivered', 'read']).count()
        delivered_messages = messages.filter(status__in=['delivered', 'read']).count()
        read_messages = messages.filter(status='read').count()
        failed_messages = messages.filter(status='failed').count()
        
        # Rates
        delivery_rate = (delivered_messages / sent_messages * 100) if sent_messages > 0 else 0
        read_rate = (read_messages / sent_messages * 100) if sent_messages > 0 else 0
        failure_rate = (failed_messages / total_messages * 100) if total_messages > 0 else 0
        
        # Timeline data (daily breakdown)
        daily_timeline = messages.annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            total=Count('id'),
            sent=Count('id', filter=Q(status__in=['sent', 'delivered', 'read'])),
            failed=Count('id', filter=Q(status='failed'))
        ).order_by('date')
        
        return Response({
            'campaign_info': {
                'id': campaign.id,
                'name': campaign.name,
                'description': campaign.description,
                'status': campaign.status,
                'created_at': campaign.created_at,
                'started_at': campaign.started_at,
                'completed_at': campaign.completed_at
            },
            'stats': {
                'total_messages': total_messages,
                'sent_messages': sent_messages,
                'delivered_messages': delivered_messages,
                'read_messages': read_messages,
                'failed_messages': failed_messages,
                'delivery_rate': delivery_rate,
                'read_rate': read_rate,
                'failure_rate': failure_rate
            },
            'daily_timeline': list(daily_timeline)
        })
    
    except Campaign.DoesNotExist:
        return Response({'error': 'Campaign not found'}, status=404)
