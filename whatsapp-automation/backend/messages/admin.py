from django.contrib import admin
from .models import MessageTemplate, SentMessage


@admin.register(MessageTemplate)
class MessageTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'message_type', 'is_active', 'created_at')
    list_filter = ('message_type', 'is_active', 'created_at')
    search_fields = ('name', 'content', 'user__email')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SentMessage)
class SentMessageAdmin(admin.ModelAdmin):
    list_display = ('recipient_phone', 'user', 'status', 'sent_at')
    list_filter = ('status', 'sent_at')
    search_fields = ('recipient_phone', 'recipient_name', 'user__email', 'message_content')
    ordering = ('-sent_at',)
    readonly_fields = ('sent_at', 'delivered_at', 'twilio_sid')
