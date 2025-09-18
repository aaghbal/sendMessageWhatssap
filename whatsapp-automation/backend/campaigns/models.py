from django.db import models
from django.contrib.auth import get_user_model
from contacts.models import PhoneNumber, PhoneNumberGroup
from whatsapp_messages.models import MessageTemplate

User = get_user_model()


class Campaign(models.Model):
    """Model to manage bulk message campaigns"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='campaigns')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    message_template = models.ForeignKey(MessageTemplate, on_delete=models.CASCADE)
    target_groups = models.ManyToManyField(PhoneNumberGroup, blank=True)
    target_phones = models.ManyToManyField(PhoneNumber, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    scheduled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_total_recipients(self):
        """Calculate total number of recipients"""
        phone_count = self.target_phones.count()
        for group in self.target_groups.all():
            phone_count += group.phone_numbers.count()
        return phone_count
    
    def get_sent_count(self):
        """Get count of sent messages for this campaign"""
        return self.campaign_messages.filter(status__in=['sent', 'delivered', 'read']).count()
    
    def get_failed_count(self):
        """Get count of failed messages for this campaign"""
        return self.campaign_messages.filter(status='failed').count()


class CampaignMessage(models.Model):
    """Model to track individual messages within a campaign"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed'),
    ]
    
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='campaign_messages')
    recipient_phone = models.CharField(max_length=25)
    recipient_name = models.CharField(max_length=100, blank=True, null=True)
    message_content = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    twilio_sid = models.CharField(max_length=100, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.campaign.name} - {self.recipient_phone}"


class CampaignAnalytics(models.Model):
    """Model to store campaign analytics"""
    campaign = models.OneToOneField(Campaign, on_delete=models.CASCADE, related_name='analytics')
    total_recipients = models.IntegerField(default=0)
    messages_sent = models.IntegerField(default=0)
    messages_delivered = models.IntegerField(default=0)
    messages_read = models.IntegerField(default=0)
    messages_failed = models.IntegerField(default=0)
    delivery_rate = models.FloatField(default=0.0)  # Percentage
    read_rate = models.FloatField(default=0.0)  # Percentage
    cost_estimate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Analytics for {self.campaign.name}"
    
    def update_analytics(self):
        """Update analytics based on campaign messages"""
        messages = self.campaign.campaign_messages.all()
        self.total_recipients = messages.count()
        self.messages_sent = messages.filter(status__in=['sent', 'delivered', 'read']).count()
        self.messages_delivered = messages.filter(status__in=['delivered', 'read']).count()
        self.messages_read = messages.filter(status='read').count()
        self.messages_failed = messages.filter(status='failed').count()
        
        # Calculate rates
        if self.messages_sent > 0:
            self.delivery_rate = (self.messages_delivered / self.messages_sent) * 100
            self.read_rate = (self.messages_read / self.messages_sent) * 100
        
        self.save()
