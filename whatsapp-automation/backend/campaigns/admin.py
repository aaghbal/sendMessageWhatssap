from django.contrib import admin
from .models import Campaign, CampaignMessage, CampaignAnalytics


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'status', 'get_total_recipients', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'description', 'user__email')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'started_at', 'completed_at')
    filter_horizontal = ('target_groups', 'target_phones')


@admin.register(CampaignMessage)
class CampaignMessageAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'recipient_phone', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('recipient_phone', 'recipient_name', 'campaign__name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'sent_at', 'delivered_at', 'twilio_sid')


@admin.register(CampaignAnalytics)
class CampaignAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'messages_sent', 'delivery_rate', 'read_rate', 'updated_at')
    list_filter = ('updated_at',)
    search_fields = ('campaign__name',)
    ordering = ('-updated_at',)
    readonly_fields = ('created_at', 'updated_at')
