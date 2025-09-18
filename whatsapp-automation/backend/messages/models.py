from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class MessageTemplate(models.Model):
    """Model to store message templates"""
    TEMPLATE_TYPES = [
        ('text', 'Text Only'),
        ('media', 'With Media'),
        ('location', 'With Location'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_templates')
    name = models.CharField(max_length=100)
    message_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES, default='text')
    content = models.TextField()
    media_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'name']
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class SentMessage(models.Model):
    """Model to track sent messages"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient_phone = models.CharField(max_length=25)
    recipient_name = models.CharField(max_length=100, blank=True, null=True)
    message_content = models.TextField()
    template_used = models.ForeignKey(MessageTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    twilio_sid = models.CharField(max_length=100, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"Message to {self.recipient_phone} - {self.status}"
